from app.extensions import db
from app.models.contest import Contest, ContestParticipant
from app.models.submission import Submission

def update_contest_rankings(contest_id):
    """Update rankings for a contest"""
    contest = Contest.query.get(contest_id)
    if not contest:
        return
    
    # Get all participants
    participants = ContestParticipant.query.filter_by(contest_id=contest_id).all()
    if not participants:
        return
    
    # Calculate scores for each participant
    for participant in participants:
        # Get all accepted submissions for this contest
        submissions = Submission.query.filter(
            Submission.user_id == participant.user_id,
            Submission.status == 'ACCEPTED',
            Submission.problem_id.in_([cp.problem_id for cp in contest.problems])
        ).all()
        
        # Calculate total score
        score = 0
        for submission in submissions:
            # Find the corresponding contest problem
            contest_problem = next((cp for cp in contest.problems if cp.problem_id == submission.problem_id), None)
            if contest_problem:
                score += contest_problem.score
        
        participant.score = score
    
    # Sort participants by score descending
    participants.sort(key=lambda p: p.score, reverse=True)
    
    # Update ranks
    rank = 1
    for i, participant in enumerate(participants):
        if i > 0 and participant.score < participants[i-1].score:
            rank = i + 1
        participant.rank = rank
    
    db.session.commit()
    return True
