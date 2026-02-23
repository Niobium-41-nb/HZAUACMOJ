from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class Role(db.Model):
    """User role model"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    
    # Relationship
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class User(db.Model, UserMixin):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default=2)  # Default to 'user' role
    real_name = db.Column(db.String(64))
    student_id = db.Column(db.String(32), unique=True, nullable=True)
    school = db.Column(db.String(128))
    college = db.Column(db.String(128))
    bio = db.Column(db.Text)
    github = db.Column(db.String(128))
    avatar = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    blog_posts = db.relationship('Blog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    blog_comments = db.relationship('BlogComment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    blog_likes = db.relationship('BlogLike', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    resources = db.relationship('Resource', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    resource_comments = db.relationship('ResourceComment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    resource_likes = db.relationship('ResourceLike', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    contest_participations = db.relationship('ContestParticipant', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def password(self):
        """Prevent password from being accessed directly"""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role.name == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'
