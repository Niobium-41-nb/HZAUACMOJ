import os
import subprocess
import tempfile
import json
from app.extensions import db, redis_client
from app.models.submission import Submission
from app.models.problem import Problem, ProblemTestcase

def judge_submission(submission_id):
    """Judge a submission"""
    submission = Submission.query.get(submission_id)
    if not submission:
        return
    
    problem = Problem.query.get(submission.problem_id)
    if not problem:
        submission.status = 'SYSTEM_ERROR'
        submission.error_message = 'Problem not found'
        db.session.commit()
        return
    
    testcases = ProblemTestcase.query.filter_by(problem_id=problem.id).all()
    if not testcases:
        submission.status = 'SYSTEM_ERROR'
        submission.error_message = 'No testcases found for this problem'
        db.session.commit()
        return
    
    # Set submission status to running
    submission.status = 'RUNNING'
    db.session.commit()
    
    try:
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to file
            if submission.language == 'python':
                code_file = os.path.join(temp_dir, 'main.py')
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(submission.code)
            elif submission.language == 'cpp':
                code_file = os.path.join(temp_dir, 'main.cpp')
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(submission.code)
            elif submission.language == 'c':
                code_file = os.path.join(temp_dir, 'main.c')
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(submission.code)
            elif submission.language == 'java':
                code_file = os.path.join(temp_dir, 'Main.java')
                with open(code_file, 'w', encoding='utf-8') as f:
                    f.write(submission.code)
            else:
                submission.status = 'SYSTEM_ERROR'
                submission.error_message = f'Unsupported language: {submission.language}'
                db.session.commit()
                return
            
            # Compile if necessary
            executable = None
            if submission.language in ['cpp', 'c']:
                executable = os.path.join(temp_dir, 'main')
                if submission.language == 'cpp':
                    compile_cmd = ['g++', '-std=c++17', '-O2', code_file, '-o', executable]
                else:
                    compile_cmd = ['gcc', '-O2', code_file, '-o', executable]
                
                try:
                    result = subprocess.run(compile_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        submission.status = 'COMPILE_ERROR'
                        submission.error_message = result.stderr
                        db.session.commit()
                        return
                except subprocess.TimeoutExpired:
                    submission.status = 'COMPILE_ERROR'
                    submission.error_message = 'Compilation timed out'
                    db.session.commit()
                    return
            elif submission.language == 'java':
                try:
                    compile_cmd = ['javac', code_file]
                    result = subprocess.run(compile_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10)
                    if result.returncode != 0:
                        submission.status = 'COMPILE_ERROR'
                        submission.error_message = result.stderr
                        db.session.commit()
                        return
                except subprocess.TimeoutExpired:
                    submission.status = 'COMPILE_ERROR'
                    submission.error_message = 'Compilation timed out'
                    db.session.commit()
                    return
            
            # Run testcases
            max_time = 0
            max_memory = 0
            all_passed = True
            error_msg = None
            
            for testcase in testcases:
                try:
                    # Run the code
                    if submission.language == 'python':
                        run_cmd = ['python3', 'main.py']
                    elif submission.language in ['cpp', 'c']:
                        run_cmd = ['./main']
                    elif submission.language == 'java':
                        run_cmd = ['java', 'Main']
                    else:
                        continue
                    
                    # Run with timeout
                    result = subprocess.run(
                        run_cmd,
                        input=testcase.input,
                        capture_output=True,
                        text=True,
                        cwd=temp_dir,
                        timeout=problem.time_limit / 1000.0
                    )
                    
                    # Check output
                    if result.stdout.strip() != testcase.output.strip():
                        all_passed = False
                        error_msg = f'Wrong Answer on testcase {testcase.id}'
                        break
                    
                    # Update stats (approximate)
                    max_time = max(max_time, result.returncode * 1000)  # Not accurate, just placeholder
                    max_memory = max(max_memory, 0)  # Not accurate, just placeholder
                    
                except subprocess.TimeoutExpired:
                    submission.status = 'TIME_LIMIT_EXCEEDED'
                    submission.execution_time = problem.time_limit
                    submission.error_message = f'Time limit exceeded (>{problem.time_limit}ms)'
                    db.session.commit()
                    return
                except Exception as e:
                    submission.status = 'RUNTIME_ERROR'
                    submission.error_message = str(e)
                    db.session.commit()
                    return
            
            # Update submission result
            if all_passed:
                submission.status = 'ACCEPTED'
                submission.execution_time = max_time
                submission.memory_used = max_memory
                
                # Update problem stats
                problem.accepted_submissions += 1
            else:
                submission.status = 'WRONG_ANSWER'
                submission.error_message = error_msg
            
            db.session.commit()
            
    except Exception as e:
        submission.status = 'SYSTEM_ERROR'
        submission.error_message = f'System error: {str(e)}'
        db.session.commit()
        return
