"""
Module to handle relationships between models after all models are defined
"""


def define_relationships(db):
    """
    Define relationships after all models are initialized
    """
    from app.models.user import User
    from app.models.voter import Voter
    from app.models.star_log import StarLog
    
    # Define relationships
    User.star_logs = db.relationship('StarLog', backref='user', lazy=True)
    Voter.star_logs = db.relationship('StarLog', backref='voter', lazy=True)