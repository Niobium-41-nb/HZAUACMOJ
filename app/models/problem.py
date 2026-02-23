from datetime import datetime
from app.extensions import db


class ProblemTag(db.Model):
    """Problem tag model"""
    __tablename__ = 'problem_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    
    def __repr__(self):
        return f'<ProblemTag {self.name}>'


class ProblemTestcase(db.Model):
    """Problem testcase model"""
    __tablename__ = 'problem_testcases'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    input = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=False)
    is_sample = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ProblemTestcase for problem {self.problem_id}>'


class Problem(db.Model):
    """Problem model"""
    __tablename__ = 'problems'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    input_description = db.Column(db.Text, nullable=False)
    output_description = db.Column(db.Text, nullable=False)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    hint = db.Column(db.Text)
    source = db.Column(db.String(128))
    time_limit = db.Column(db.Integer, default=1000)  # in milliseconds
    memory_limit = db.Column(db.Integer, default=256)  # in megabytes
    total_submissions = db.Column(db.Integer, default=0)
    accepted_submissions = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    testcases = db.relationship('ProblemTestcase', backref='problem', lazy='dynamic', cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='problem', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('ProblemTag', secondary='problem_tag_association', backref=db.backref('problems', lazy='dynamic'))
    contest_problems = db.relationship('ContestProblem', backref='problem', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Problem {self.id}: {self.title}>'


# Association table for problem and tag (many-to-many)
problem_tag_association = db.Table('problem_tag_association',
    db.Column('problem_id', db.Integer, db.ForeignKey('problems.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('problem_tags.id'), primary_key=True)
)
