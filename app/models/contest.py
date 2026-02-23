from datetime import datetime
from app.extensions import db


class ContestProblem(db.Model):
    """Contest problem model"""
    __tablename__ = 'contest_problems'
    
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, default=100)
    
    # Relationship
    problem = db.relationship('Problem', backref=db.backref('contest_problems', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ContestProblem {self.id}>'


class ContestParticipant(db.Model):
    """Contest participant model"""
    __tablename__ = 'contest_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('contest_participations', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ContestParticipant {self.user_id} in contest {self.contest_id}>'


class Contest(db.Model):
    """Contest model"""
    __tablename__ = 'contests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    problems = db.relationship('ContestProblem', backref='contest', lazy='dynamic', cascade='all, delete-orphan')
    participants = db.relationship('ContestParticipant', backref='contest', lazy='dynamic', cascade='all, delete-orphan')
    
    def is_active(self):
        """Check if contest is currently active"""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time
    
    def has_started(self):
        """Check if contest has started"""
        return datetime.utcnow() >= self.start_time
    
    def has_ended(self):
        """Check if contest has ended"""
        return datetime.utcnow() > self.end_time
    
    def __repr__(self):
        return f'<Contest {self.title}>'
