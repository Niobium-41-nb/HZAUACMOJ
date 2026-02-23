from datetime import datetime
from app.extensions import db


class Submission(db.Model):
    """Submission model"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(32), nullable=False)  # e.g., 'c', 'cpp', 'python', 'java'
    status = db.Column(db.String(32), default='PENDING')  # PENDING, RUNNING, ACCEPTED, WRONG_ANSWER, TIME_LIMIT_EXCEEDED, MEMORY_LIMIT_EXCEEDED, COMPILE_ERROR, RUNTIME_ERROR, SYSTEM_ERROR
    execution_time = db.Column(db.Integer, default=0)  # in milliseconds
    memory_used = db.Column(db.Integer, default=0)  # in kilobytes
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Submission {self.id} for problem {self.problem_id} by user {self.user_id}>'
