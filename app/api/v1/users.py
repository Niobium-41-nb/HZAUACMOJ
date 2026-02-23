from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user import User, Role


api = Namespace('users', description='User operations')

# Model definitions
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email'),
    'role': fields.String(description='User role'),
    'real_name': fields.String(description='Real name'),
    'student_id': fields.String(description='Student ID'),
    'school': fields.String(description='School'),
    'college': fields.String(description='College'),
    'bio': fields.String(description='Bio'),
    'github': fields.String(description='GitHub URL'),
    'avatar': fields.String(description='Avatar URL'),
    'is_active': fields.Boolean(description='Is active'),
    'created_at': fields.DateTime(readonly=True, description='Created at'),
    'last_login': fields.DateTime(readonly=True, description='Last login')
})

user_update_model = api.model('UserUpdate', {
    'email': fields.String(description='Email'),
    'real_name': fields.String(description='Real name'),
    'student_id': fields.String(description='Student ID'),
    'school': fields.String(description='School'),
    'college': fields.String(description='College'),
    'bio': fields.String(description='Bio'),
    'github': fields.String(description='GitHub URL'),
    'avatar': fields.String(description='Avatar URL')
})

@api.route('/')
class UserList(Resource):
    """User list resource"""
    
    @login_required
    @api.marshal_list_with(user_model)
    def get(self):
        """Get all users (admin only)"""
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.order_by(User.id).paginate(page=page, per_page=per_page)
        return users.items, 200


@api.route('/<int:user_id>')
class UserDetail(Resource):
    """User detail resource"""
    
    @api.marshal_with(user_model)
    def get(self, user_id):
        """Get a user by ID"""
        user = User.query.get_or_404(user_id)
        return user, 200
    
    @login_required
    @api.expect(user_update_model)
    @api.marshal_with(user_model)
    def put(self, user_id):
        """Update a user"""
        user = User.query.get_or_404(user_id)
        
        # Only the user themselves or admin can update
        if user.id != current_user.id and not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        data = request.get_json()
        
        # Update user fields
        user.email = data.get('email', user.email)
        
        # Only allow updating these fields if it's the user themselves or admin
        if user.id == current_user.id or current_user.is_admin():
            user.real_name = data.get('real_name', user.real_name)
            user.student_id = data.get('student_id', user.student_id)
            user.school = data.get('school', user.school)
            user.college = data.get('college', user.college)
            user.bio = data.get('bio', user.bio)
            user.github = data.get('github', user.github)
            user.avatar = data.get('avatar', user.avatar)
        
        # Only admin can update role and active status
        if current_user.is_admin():
            user.role = data.get('role', user.role)
            user.is_active = data.get('is_active', user.is_active)
        
        db.session.commit()
        
        return user, 200
    
    @login_required
    def delete(self, user_id):
        """Delete a user"""
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        user = User.query.get_or_404(user_id)
        
        db.session.delete(user)
        db.session.commit()
        
        return {'message': 'User deleted successfully'}, 200


@api.route('/me')
class CurrentUser(Resource):
    """Current user resource"""
    
    @login_required
    @api.marshal_with(user_model)
    def get(self):
        """Get current user information"""
        return current_user, 200
    
    @login_required
    @api.expect(user_update_model)
    @api.marshal_with(user_model)
    def put(self):
        """Update current user information"""
        data = request.get_json()
        
        # Update current user fields
        current_user.email = data.get('email', current_user.email)
        current_user.real_name = data.get('real_name', current_user.real_name)
        current_user.student_id = data.get('student_id', current_user.student_id)
        current_user.school = data.get('school', current_user.school)
        current_user.college = data.get('college', current_user.college)
        current_user.bio = data.get('bio', current_user.bio)
        current_user.github = data.get('github', current_user.github)
        current_user.avatar = data.get('avatar', current_user.avatar)
        
        db.session.commit()
        
        return current_user, 200


@api.route('/roles')
class RoleList(Resource):
    """Role list resource"""
    
    @login_required
    @api.marshal_list_with(api.model('Role', {
        'id': fields.Integer(readonly=True, description='Role ID'),
        'name': fields.String(required=True, description='Role name'),
        'description': fields.String(description='Role description')
    }))
    def get(self):
        """Get all roles"""
        if not current_user.is_admin():
            api.abort(403, 'Permission denied')
        
        roles = Role.query.all()
        return roles, 200
