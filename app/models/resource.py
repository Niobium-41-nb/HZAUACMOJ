from datetime import datetime
from app.extensions import db


class ResourceTag(db.Model):
    """Resource tag model"""
    __tablename__ = 'resource_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    
    def __repr__(self):
        return f'<ResourceTag {self.name}>'


class ResourceComment(db.Model):
    """Resource comment model"""
    __tablename__ = 'resource_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('resource_comments', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ResourceComment {self.id}>'


class ResourceLike(db.Model):
    """Resource like model"""
    __tablename__ = 'resource_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('resource_likes', lazy='dynamic'))
    resource = db.relationship('Resource', backref=db.backref('likes', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<ResourceLike {self.id}>'


class Resource(db.Model):
    """Resource model"""
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('resources', lazy='dynamic'))
    comments = db.relationship('ResourceComment', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('ResourceTag', secondary='resource_tag_association', backref=db.backref('resources', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Resource {self.title}>'


# Association table for resource and tag (many-to-many)
resource_tag_association = db.Table('resource_tag_association',
    db.Column('resource_id', db.Integer, db.ForeignKey('resources.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('resource_tags.id'), primary_key=True)
)
