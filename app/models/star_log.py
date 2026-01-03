from datetime import datetime
from app.database import db


class StarLog(db.Model):
    __tablename__ = 'star_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.Enum('ADD', 'EDIT', 'DELETE', name='star_actions'), nullable=False)  # ADD, EDIT, DELETE
    old_rating = db.Column(db.Integer, nullable=True)  # Previous rating (for EDIT/DELETE)
    new_rating = db.Column(db.Integer, nullable=True)  # New rating (for ADD/EDIT)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<StarLog {self.action} on Voter {self.voter_id} by User {self.user_id}>'