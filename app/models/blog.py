from datetime import datetime
from app.extensions import db


class BlogTag(db.Model):
    """Blog tag model"""
    __tablename__ = 'blog_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    
    def __repr__(self):
        return f'<BlogTag {self.name}>'


class BlogComment(db.Model):
    """Blog comment model"""
    __tablename__ = 'blog_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('blog_comments', lazy='dynamic'))
    
    def __repr__(self):
        return f'<BlogComment {self.id}>'


class BlogLike(db.Model):
    """Blog like model"""
    __tablename__ = 'blog_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('blog_likes', lazy='dynamic'))
    blog = db.relationship('Blog', backref=db.backref('likes', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<BlogLike {self.id}>'


class Blog(db.Model):
    """Blog model"""
    __tablename__ = 'blogs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    views = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('blog_posts', lazy='dynamic'))
    comments = db.relationship('BlogComment', backref='blog', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('BlogTag', secondary='blog_tag_association', backref=db.backref('blogs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Blog {self.title}>'


# Association table for blog and tag (many-to-many)
blog_tag_association = db.Table('blog_tag_association',
    db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('blog_tags.id'), primary_key=True)
)
