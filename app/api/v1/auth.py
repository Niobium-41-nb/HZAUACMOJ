from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User


api = Namespace('auth', description='Authentication operations')

# Model definitions
auth_model = api.model('Auth', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email'),
    'real_name': fields.String(description='Real name'),
    'student_id': fields.String(description='Student ID'),
    'role': fields.String(description='User role')
})

@api.route('/login')
class Login(Resource):
    """Login resource"""
    
    @api.expect(auth_model)
    @api.marshal_with(user_model)
    def post(self):
        """Login a user"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return user, 200
        
        api.abort(401, 'Invalid username or password')


@api.route('/logout')
class Logout(Resource):
    """Logout resource"""
    
    @login_required
    def post(self):
        """Logout a user"""
        logout_user()
        return {'message': 'Successfully logged out'}, 200


@api.route('/register')
class Register(Resource):
    """Register resource"""
    
    @api.expect(api.model('Register', {
        'username': fields.String(required=True, description='Username'),
        'email': fields.String(required=True, description='Email'),
        'password': fields.String(required=True, description='Password'),
        'real_name': fields.String(description='Real name'),
        'student_id': fields.String(description='Student ID')
    }))
    @api.marshal_with(user_model)
    def post(self):
        """Register a new user"""
        data = request.get_json()
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            api.abort(400, 'Username already exists')
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            api.abort(400, 'Email already exists')
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            real_name=data.get('real_name'),
            student_id=data.get('student_id')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, 201


@api.route('/current')
class CurrentUser(Resource):
    """Current user resource"""
    
    @login_required
    @api.marshal_with(user_model)
    def get(self):
        """Get current user information"""
        return current_user, 200
