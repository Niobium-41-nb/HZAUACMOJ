from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from app.extensions import db
from app.models.problem import Problem, ProblemTag, ProblemTestcase
from app.models.submission import Submission


api = Namespace('problems', description='Problem operations')

# Model definitions
problem_tag_model = api.model('ProblemTag', {
    'id': fields.Integer(readonly=True, description='Tag ID'),
    'name': fields.String(required=True, description='Tag name'),
    'description': fields.String(description='Tag description')
})

problem_testcase_model = api.model('ProblemTestcase', {
    'id': fields.Integer(readonly=True, description='Testcase ID'),
    'problem_id': fields.Integer(description='Problem ID'),
    'input': fields.String(description='Testcase input'),
    'output': fields.String(description='Testcase output'),
    'is_sample': fields.Boolean(description='Is sample testcase')
})

problem_model = api.model('Problem', {
    'id': fields.Integer(readonly=True, description='Problem ID'),
    'title': fields.String(required=True, description='Problem title'),
    'description': fields.String(required=True, description='Problem description'),
    'input_description': fields.String(required=True, description='Input description'),
    'output_description': fields.String(required=True, description='Output description'),
    'sample_input': fields.String(description='Sample input'),
    'sample_output': fields.String(description='Sample output'),
    'hint': fields.String(description='Hint'),
    'source': fields.String(description='Problem source'),
    'time_limit': fields.Integer(description='Time limit (ms)'),
    'memory_limit': fields.Integer(description='Memory limit (MB)'),
    'total_submissions': fields.Integer(readonly=True, description='Total submissions'),
    'accepted_submissions': fields.Integer(readonly=True, description='Accepted submissions'),
    'is_public': fields.Boolean(description='Is public'),
    'created_at': fields.DateTime(readonly=True, description='Created at'),
    'updated_at': fields.DateTime(readonly=True, description='Updated at'),
    'tags': fields.List(fields.Nested(problem_tag_model), description='Problem tags')
})

@api.route('/')
class ProblemList(Resource):
    """Problem list resource"""
    
    @api.marshal_list_with(problem_model)
    def get(self):
        """Get all public problems"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        problems = Problem.query.filter_by(is_public=True).order_by(Problem.id).paginate(page=page, per_page=per_page)
        return problems.items, 200
    
    @login_required
    @api.expect(problem_model)
    @api.marshal_with(problem_model)
    def post(self):
        """Create a new problem"""
        # Only admins can create problems
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        new_problem = Problem(
            title=data['title'],
            description=data['description'],
            input_description=data['input_description'],
            output_description=data['output_description'],
            sample_input=data.get('sample_input'),
            sample_output=data.get('sample_output'),
            hint=data.get('hint'),
            source=data.get('source'),
            time_limit=data.get('time_limit', 1000),
            memory_limit=data.get('memory_limit', 256),
            is_public=data.get('is_public', False)
        )
        
        # Add tags if provided
        if 'tags' in data:
            for tag_data in data['tags']:
                tag = ProblemTag.query.filter_by(name=tag_data['name']).first()
                if tag:
                    new_problem.tags.append(tag)
        
        db.session.add(new_problem)
        db.session.commit()
        
        return new_problem, 201


@api.route('/<int:problem_id>')
class ProblemDetail(Resource):
    """Problem detail resource"""
    
    @api.marshal_with(problem_model)
    def get(self, problem_id):
        """Get a problem by ID"""
        problem = Problem.query.get_or_404(problem_id)
        
        # Check if problem is public or user is admin
        if not problem.is_public and (not current_user.is_authenticated or not current_user.is_admin()):
            api.abort(403, 'Permission denied')
        
        return problem, 200
    
    @login_required
    @api.expect(problem_model)
    @api.marshal_with(problem_model)
    def put(self, problem_id):
        """Update a problem"""
        # Only admins can update problems
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        problem = Problem.query.get_or_404(problem_id)
        data = request.get_json()
        
        # Update problem fields
        problem.title = data.get('title', problem.title)
        problem.description = data.get('description', problem.description)
        problem.input_description = data.get('input_description', problem.input_description)
        problem.output_description = data.get('output_description', problem.output_description)
        problem.sample_input = data.get('sample_input', problem.sample_input)
        problem.sample_output = data.get('sample_output', problem.sample_output)
        problem.hint = data.get('hint', problem.hint)
        problem.source = data.get('source', problem.source)
        problem.time_limit = data.get('time_limit', problem.time_limit)
        problem.memory_limit = data.get('memory_limit', problem.memory_limit)
        problem.is_public = data.get('is_public', problem.is_public)
        
        # Update tags if provided
        if 'tags' in data:
            problem.tags.clear()
            for tag_data in data['tags']:
                tag = ProblemTag.query.filter_by(name=tag_data['name']).first()
                if tag:
                    problem.tags.append(tag)
        
        db.session.commit()
        
        return problem, 200
    
    @login_required
    def delete(self, problem_id):
        """Delete a problem"""
        # Only admins can delete problems
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        problem = Problem.query.get_or_404(problem_id)
        
        db.session.delete(problem)
        db.session.commit()
        
        return {'message': 'Problem deleted successfully'}, 200


@api.route('/<int:problem_id>/testcases')
class ProblemTestcaseList(Resource):
    """Problem testcase list resource"""
    
    @login_required
    @api.marshal_list_with(problem_testcase_model)
    def get(self, problem_id):
        """Get all testcases for a problem"""
        # Only admins or problem creator can view all testcases
        problem = Problem.query.get_or_404(problem_id)
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        testcases = ProblemTestcase.query.filter_by(problem_id=problem_id).all()
        return testcases, 200
    
    @login_required
    @api.expect(problem_testcase_model)
    @api.marshal_with(problem_testcase_model)
    def post(self, problem_id):
        """Add a testcase to a problem"""
        # Only admins can add testcases
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        new_testcase = ProblemTestcase(
            problem_id=problem_id,
            input=data.get('input', ''),
            output=data.get('output', ''),
            is_sample=data.get('is_sample', False)
        )
        
        db.session.add(new_testcase)
        db.session.commit()
        
        return new_testcase, 201


@api.route('/tags')
class ProblemTagList(Resource):
    """Problem tag list resource"""
    
    @api.marshal_list_with(problem_tag_model)
    def get(self):
        """Get all problem tags"""
        tags = ProblemTag.query.all()
        return tags, 200
    
    @login_required
    @api.expect(problem_tag_model)
    @api.marshal_with(problem_tag_model)
    def post(self):
        """Create a new problem tag"""
        # Only admins can create tags
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        # Check if tag already exists
        if ProblemTag.query.filter_by(name=data['name']).first():
            api.abort(400, 'Tag already exists')
        
        new_tag = ProblemTag(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(new_tag)
        db.session.commit()
        
        return new_tag, 201
