import pandas as pd
from app.models.voter import Voter
from app import db


def validate_excel_columns(df):
    """
    Validate that the Excel file has the required columns
    """
    required_columns = ['voter_id']
    available_columns = [col.lower().strip() for col in df.columns]
    
    # Check if any of the required columns exist (case insensitive)
    for req_col in required_columns:
        if req_col not in available_columns:
            # Check for common variations
            variations = [req_col.replace('_', ' '), f'{req_col}s']
            found = any(var in available_columns for var in variations)
            if not found:
                return False, f"Required column '{req_col}' not found in Excel file"
    
    return True, "Valid"


def normalize_column_names(df):
    """
    Normalize column names to match our database fields
    """
    column_mapping = {
        'sr no': 'sr_no',
        'sr_no': 'sr_no',
        'booth no': 'booth_no',
        'booth_no': 'booth_no',
        'booth no.': 'booth_no',
        'booth_no.': 'booth_no',
        'voter id': 'voter_id',
        'voter_id': 'voter_id',
        'voterid': 'voter_id',
        'voter id.': 'voter_id',
        'voter_id.': 'voter_id',
        'name': 'full_name',  # Map general 'name' to full_name instead of first_name to avoid booth names
        'full name': 'full_name',
        'full_name': 'full_name',
        'complete name': 'full_name',
        'first name': 'first_name',
        'first_name': 'first_name',
        'englishname': 'first_name',
        'english_name': 'first_name',
        'middle name': 'father_name',
        'middle_name': 'father_name',
        'father name': 'father_name',
        'father_name': 'father_name',
        'mother name': 'father_name',
        'surname': 'surname',
        'last name': 'surname',
        'last_name': 'surname',
        'mobile number': 'mobile_no',
        'mobile_no': 'mobile_no',
        'mobile no': 'mobile_no',
        'mobile_no.': 'mobile_no',
        'mobile no.': 'mobile_no',
        'phone': 'mobile_no',
        'phone number': 'mobile_no',
        'yadibhag no': 'yadibhag_no',
        'yadibhag_no': 'yadibhag_no',
        'yadibhag no.': 'yadibhag_no',
        'yadibhagno': 'yadibhag_no',
        'yadibhag name': 'yadibhag_name',
        'yadibhag_name': 'yadibhag_name',
        'yadibhagname': 'yadibhag_name',
        'voter srno': 'voter_srno',
        'voter_srno': 'voter_srno',
        'voter serial': 'voter_srno',
        'voter_serial': 'voter_srno',
        'age': 'age',
        'gender': 'gender',
        'voting card no': 'voting_card_no',
        'voting_card_no': 'voting_card_no',
        'voting card no.': 'voting_card_no',
        'votingcardno': 'voting_card_no',
        'karyakarta': 'karyakarta',
        'worker': 'karyakarta',
    }
    
    # Create a new mapping dict with actual column names from the dataframe
    normalized_mapping = {}
    for col in df.columns:
        normalized_col = col.lower().strip()
        if normalized_col in column_mapping:
            normalized_mapping[col] = column_mapping[normalized_col]
    
    return df.rename(columns=normalized_mapping)


def process_voter_data(df):
    """
    Process the Excel data and convert to voter objects
    """
    # Normalize column names
    df = normalize_column_names(df)
    
    # Process each row
    voters_data = []
    for index, row in df.iterrows():
        voter_data = {
            'voter_id': str(row.get('voter_id', '')).strip() if pd.notna(row.get('voter_id', '')) else '',
            'booth_no': int(row.get('booth_no')) if pd.notna(row.get('booth_no')) and row.get('booth_no') is not None else None,
            'first_name': str(row.get('first_name', '')).strip() if pd.notna(row.get('first_name', '')) else '',
            'father_name': str(row.get('father_name', '')).strip() if pd.notna(row.get('father_name', '')) else '',
            'surname': str(row.get('surname', '')).strip() if pd.notna(row.get('surname', '')) else '',
            'full_name': str(row.get('full_name', '')).strip() if pd.notna(row.get('full_name', '')) else '',
            'mobile_no': str(row.get('mobile_no', '')).strip() if pd.notna(row.get('mobile_no', '')) else '',
            'yadibhag_no': str(row.get('yadibhag_no', '')).strip() if pd.notna(row.get('yadibhag_no', '')) else '',
            'yadibhag_name': str(row.get('yadibhag_name', '')).strip() if pd.notna(row.get('yadibhag_name', '')) else '',
            'voter_srno': str(row.get('voter_srno', '')).strip() if pd.notna(row.get('voter_srno', '')) else '',
            'age': int(row.get('age')) if pd.notna(row.get('age')) and row.get('age') is not None else None,
            'gender': str(row.get('gender', '')).strip() if pd.notna(row.get('gender', '')) else '',
            'voting_card_no': str(row.get('voting_card_no', '')).strip() if pd.notna(row.get('voting_card_no', '')) else '',
            'karyakarta': str(row.get('karyakarta', '')).strip() if pd.notna(row.get('karyakarta', '')) else ''
        }
        
        # Validate required fields
        if not voter_data['voter_id']:
            continue  # Skip rows without voter_id
            
        voters_data.append(voter_data)
    
    return voters_data