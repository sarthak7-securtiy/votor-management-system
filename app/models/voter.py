from datetime import datetime
from app.database import db


class Voter(db.Model):
    __tablename__ = 'voters'
    
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(100), unique=True, nullable=False)  # Voter ID from Excel
    booth_no = db.Column(db.Integer, nullable=True)  # Booth Number
    first_name = db.Column(db.String(100), nullable=True)  # First Name
    father_name = db.Column(db.String(100), nullable=True)  # Father's Name
    surname = db.Column(db.String(100), nullable=True)  # Surname
    full_name = db.Column(db.String(200), nullable=True)  # Full Name
    mobile_no = db.Column(db.String(15), nullable=True)  # Mobile Number
    star_rating = db.Column(db.Integer, default=0)  # Star rating (0-5)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Additional fields from Excel
    yadibhag_no = db.Column(db.String(50), nullable=True)  # Yadibhag Number
    yadibhag_name = db.Column(db.String(200), nullable=True)  # Yadibhag Name
    voter_srno = db.Column(db.String(50), nullable=True)  # Voter Serial Number
    age = db.Column(db.Integer, nullable=True)  # Age
    gender = db.Column(db.String(10), nullable=True)  # Gender
    voting_card_no = db.Column(db.String(50), nullable=True)  # Voting Card Number
    karyakarta = db.Column(db.String(100), nullable=True)  # Karyakarta

    # Relationship with star logs
    star_logs = db.relationship('StarLog', backref='voter', lazy=True)

    def __repr__(self):
        return f'<Voter {self.full_name} (ID: {self.voter_id})>'

    def get_display_name(self):
        """Return the most complete name available"""
        # Check if first_name contains booth name (non-name text)
        if self.full_name and not self._is_booth_name(self.full_name):
            return self.full_name
        elif self.first_name and self.surname and not self._is_booth_name(self.first_name) and not self._is_booth_name(self.surname):
            return f"{self.first_name} {self.surname}"
        elif self.first_name and not self._is_booth_name(self.first_name):
            return self.first_name
        elif self.surname and not self._is_booth_name(self.surname):
            return self.surname
        else:
            return f"Voter {self.voter_id}"
    
    def _is_booth_name(self, text):
        """Check if text looks like a booth name rather than a person's name"""
        booth_indicators = ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको']
        text_lower = text.lower().strip()
        return any(indicator in text_lower for indicator in booth_indicators)
            
    def get_star_display(self):
        """Return star rating as visual stars (★)"""
        if self.star_rating <= 0:
            return ""
        elif self.star_rating >= 5:
            return "★★★★★"
        else:
            return "★" * self.star_rating