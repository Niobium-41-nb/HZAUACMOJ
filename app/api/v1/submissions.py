from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from app.extensions import db
from app.models.submission import Submission
from app.models.problem import Problem
from app.services.judge import judge_submission


api = Namespace('submissions', description='Submission operations')

# Model definitions
submission_model = api.model('Submission', {
    'id': fields.Integer(readonly=True, description='Submission ID'),
    'problem_id': fields.Integer(required=True, description='Problem ID'),
    'user_id': fields.Integer(description='User ID'),
    'code': fields.String(required=True, description='Submission code'),
    'language': fields.String(required=True, description='Programming language'),
    'status': fields.String(readonly=True, description='Submission status'),
    'execution_time': fields.Integer(readonly=True, description='Execution time (ms)'),
    'memory_used': fields.Integer(readonly=True, description='Memory used (KB)'),
    'error_message': fields.String(readonly=True, description='Error message'),
    'created_at': fields.DateTime(readonly=True, description='Created at')
})

@api.route('/')
class SubmissionList(Resource):
    """Submission list resource"""
    
    @api.marshal_list_with(submission_model)
    def get(self):
        """Get all submissions"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        problem_id = request.args.get('problem_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        query = Submission.query
        
        if problem_id:
            query = query.filter_by(problem_id=problem_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        submissions = query.order_by(Submission.created_at.desc()).paginate(page=page, per_page=per_page)
        return submissions.items, 200
    
    @login_required
    @api.expect(api.model('SubmissionCreate', {
        'problem_id': fields.Integer(required=True, description='Problem ID'),
        'code': fields.String(required=True, description='Submission code'),
        'language': fields.String(required=True, description='Programming language')
    }))
    @api.marshal_with(submission_model)
    def post(self):
        """Create a new submission"""
        data = request.get_json()
        
        # Check if problem exists
        problem = Problem.query.get_or_404(data['problem_id'])
        
        # Create submission
        new_submission = Submission(
            problem_id=data['problem_id'],
            user_id=current_user.id,
            code=data['code'],
            language=data['language'],
            status='PENDING',
            execution_time=0,
            memory_used=0
        )
        
        db.session.add(new_submission)
        db.session.commit()
        
        # Update problem submission counts
        problem.total_submissions += 1
        db.session.commit()
        
        # Start judge task
        judge_submission(new_submission.id)
        
        return new_submission, 201


@api.route('/<int:submission_id>')
class SubmissionDetail(Resource):
    """Submission detail resource"""
    
    @api.marshal_with(submission_model)
    def get(self, submission_id):
        """Get a submission by ID"""
        submission = Submission.query.get_or_404(submission_id)
        
        # Check if user is the owner or admin, otherwise hide code
        if submission.user_id != current_user.id and not current_user.is_admin():
            submission.code = 'Hidden'
        
        return submission, 200
    
    @login_required
    def delete(self, submission_id):
        """Delete a submission"""
        submission = Submission.query.get_or_404(submission_id)
        
        # Only admins or the owner can delete a submission
        if submission.user_id != current_user.id and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        db.session.delete(submission)
        db.session.commit()
        
        return {'message': 'Submission deleted successfully'}, 200


@api.route('/user')
class UserSubmissionList(Resource):
    """User submission list resource"""
    
    @login_required
    @api.marshal_list_with(submission_model)
    def get(self):
        """Get all submissions for the current user"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        problem_id = request.args.get('problem_id', type=int)
        
        query = Submission.query.filter_by(user_id=current_user.id)
        
        if problem_id:
            query = query.filter_by(problem_id=problem_id)
        
        submissions = query.order_by(Submission.created_at.desc()).paginate(page=page, per_page=per_page)
        return submissions.items, 200
