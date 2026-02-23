from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from app.extensions import db
from app.models.contest import Contest, ContestProblem, ContestParticipant
from app.models.problem import Problem
from app.models.user import User


api = Namespace('contests', description='Contest operations')

# Model definitions
contest_problem_model = api.model('ContestProblem', {
    'id': fields.Integer(readonly=True, description='Contest problem ID'),
    'contest_id': fields.Integer(description='Contest ID'),
    'problem_id': fields.Integer(description='Problem ID'),
    'problem_title': fields.String(readonly=True, description='Problem title'),
    'order': fields.Integer(description='Display order'),
    'score': fields.Integer(description='Problem score')
})

contest_model = api.model('Contest', {
    'id': fields.Integer(readonly=True, description='Contest ID'),
    'title': fields.String(required=True, description='Contest title'),
    'description': fields.String(description='Contest description'),
    'start_time': fields.DateTime(required=True, description='Start time'),
    'end_time': fields.DateTime(required=True, description='End time'),
    'is_public': fields.Boolean(description='Is public'),
    'created_at': fields.DateTime(readonly=True, description='Created at'),
    'updated_at': fields.DateTime(readonly=True, description='Updated at'),
    'problems': fields.List(fields.Nested(contest_problem_model), description='Contest problems')
})

contest_participant_model = api.model('ContestParticipant', {
    'id': fields.Integer(readonly=True, description='Participant ID'),
    'contest_id': fields.Integer(description='Contest ID'),
    'user_id': fields.Integer(description='User ID'),
    'score': fields.Integer(description='Total score'),
    'rank': fields.Integer(description='Rank'),
    'created_at': fields.DateTime(readonly=True, description='Joined at')
})

@api.route('/')
class ContestList(Resource):
    """Contest list resource"""
    
    @api.marshal_list_with(contest_model)
    def get(self):
        """Get all contests"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Filter by public contests or all if user is admin
        query = Contest.query
        if not current_user.is_authenticated or not current_user.is_admin():
            query = query.filter_by(is_public=True)
        
        contests = query.order_by(Contest.start_time.desc()).paginate(page=page, per_page=per_page)
        return contests.items, 200
    
    @login_required
    @api.expect(contest_model)
    @api.marshal_with(contest_model)
    def post(self):
        """Create a new contest"""
        # Only admins can create contests
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        new_contest = Contest(
            title=data['title'],
            description=data.get('description'),
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_public=data.get('is_public', False)
        )
        
        # Add problems if provided
        if 'problems' in data:
            for i, problem_data in enumerate(data['problems']):
                contest_problem = ContestProblem(
                    problem_id=problem_data['problem_id'],
                    order=i,
                    score=problem_data.get('score', 100)
                )
                new_contest.problems.append(contest_problem)
        
        db.session.add(new_contest)
        db.session.commit()
        
        return new_contest, 201


@api.route('/<int:contest_id>')
class ContestDetail(Resource):
    """Contest detail resource"""
    
    @api.marshal_with(contest_model)
    def get(self, contest_id):
        """Get a contest by ID"""
        contest = Contest.query.get_or_404(contest_id)
        
        # Check if contest is public or user is admin
        if not contest.is_public and (not current_user.is_authenticated or not current_user.is_admin()):
            api.abort(403, 'Permission denied')
        
        return contest, 200
    
    @login_required
    @api.expect(contest_model)
    @api.marshal_with(contest_model)
    def put(self, contest_id):
        """Update a contest"""
        # Only admins can update contests
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        contest = Contest.query.get_or_404(contest_id)
        data = request.get_json()
        
        # Update contest fields
        contest.title = data.get('title', contest.title)
        contest.description = data.get('description', contest.description)
        contest.start_time = data.get('start_time', contest.start_time)
        contest.end_time = data.get('end_time', contest.end_time)
        contest.is_public = data.get('is_public', contest.is_public)
        
        # Update problems if provided
        if 'problems' in data:
            # Clear existing problems
            contest.problems.clear()
            
            # Add new problems
            for i, problem_data in enumerate(data['problems']):
                contest_problem = ContestProblem(
                    problem_id=problem_data['problem_id'],
                    order=i,
                    score=problem_data.get('score', 100)
                )
                contest.problems.append(contest_problem)
        
        db.session.commit()
        
        return contest, 200
    
    @login_required
    def delete(self, contest_id):
        """Delete a contest"""
        # Only admins can delete contests
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        contest = Contest.query.get_or_404(contest_id)
        
        db.session.delete(contest)
        db.session.commit()
        
        return {'message': 'Contest deleted successfully'}, 200


@api.route('/<int:contest_id>/participants')
class ContestParticipantList(Resource):
    """Contest participant list resource"""
    
    @api.marshal_list_with(contest_participant_model)
    def get(self, contest_id):
        """Get all participants for a contest"""
        participants = ContestParticipant.query.filter_by(contest_id=contest_id).order_by(ContestParticipant.score.desc(), ContestParticipant.rank).all()
        return participants, 200
    
    @login_required
    @api.marshal_with(contest_participant_model)
    def post(self, contest_id):
        """Join a contest"""
        contest = Contest.query.get_or_404(contest_id)
        
        # Check if user is already participating
        if ContestParticipant.query.filter_by(contest_id=contest_id, user_id=current_user.id).first():
            api.abort(400, 'Already participating in this contest')
        
        # Check if contest is public or user is admin
        if not contest.is_public and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        new_participant = ContestParticipant(
            contest_id=contest_id,
            user_id=current_user.id,
            score=0,
            rank=0
        )
        
        db.session.add(new_participant)
        db.session.commit()
        
        return new_participant, 201
