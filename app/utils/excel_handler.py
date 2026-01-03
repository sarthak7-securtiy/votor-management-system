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
        'voter id': 'voter_id',
        'voter_id': 'voter_id',
        'name': 'first_name',
        'first name': 'first_name',
        'first_name': 'first_name',
        'father name': 'father_name',
        'father_name': 'father_name',
        'surname': 'surname',
        'last name': 'surname',
        'last_name': 'surname',
        'full name': 'full_name',
        'full_name': 'full_name',
        'mobile number': 'mobile_no',
        'mobile_no': 'mobile_no',
        'mobile': 'mobile_no',
        'phone': 'mobile_no',
        'phone number': 'mobile_no',
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
            'mobile_no': str(row.get('mobile_no', '')).strip() if pd.notna(row.get('mobile_no', '')) else ''
        }
        
        # Validate required fields
        if not voter_data['voter_id']:
            continue  # Skip rows without voter_id
            
        voters_data.append(voter_data)
    
    return voters_data