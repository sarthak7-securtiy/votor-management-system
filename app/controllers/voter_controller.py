from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.voter import Voter
from app.models.user import User
from app.models.star_log import StarLog
from app.database import db
import pandas as pd
import os
from werkzeug.utils import secure_filename
import re

voter_bp = Blueprint('voter', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_excel_file(file_path):
    """Process Excel file and extract voter data without restrictions"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Check if voter ID column exists
        voter_id_column_found = False
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(keyword in col_lower for keyword in ['voter', 'id', 'voterid', 'voter_id', 'voter id', 'srno', 'voter srno', 'voter_srno', 'votersrno', 'voting card no', 'voting card no.', 'voting_card_no']):
                voter_id_column_found = True
                break
        
        if not voter_id_column_found:
            raise ValueError('No Voter ID column found in Excel file. Please include a column with voter identification (e.g., voter_id, srno, voting card no, etc.)')
        
        # Get all column names and map them to our expected fields based on similarity
        column_mapping = {}
        available_columns = [col.lower().strip() for col in df.columns]
        
        # Map available columns to our expected fields
        field_keywords = {
            'voter_id': ['voter', 'id', 'voterid', 'voter_id', 'voter id', 'srno', 'voter srno', 'voter_srno', 'votersrno', 'voting card no', 'voting card no.', 'voting_card_no', 'voting card no.', 'votingcardno'],
            'booth_no': ['booth no.', 'booth_no', 'booth no', 'boothno', 'booth no.', 'booth_no.', 'booth'],
            'first_name': ['englishname', 'english_name', 'first', 'first_name', 'first name'],  # Prioritize EnglishName for actual names
            'father_name': ['middle', 'middle_name', 'middle name', 'father', 'father_name', 'father name'],
            'surname': ['last name', 'surname', 'last', 'last_name', 'last name'],
            'full_name': ['full name', 'full_name', 'fullname', 'complete name'],  # Don't map general 'name' or yadibhag name to full name
            'mobile_no': ['mobile no.', 'mobile number', 'phone', 'mobile', 'phone number', 'mobile_no.', 'mobile no', 'mobile_no'],
            'yadibhag_no': ['yadibhag no', 'yadibhag_no', 'yadibhag no.', 'yadibhag', 'yadi no', 'yadi_no'],
            'yadibhag_name': ['yadibhag name', 'yadibhag_name', 'yadibhag name', 'yadibhagname', 'yadi name', 'yadi_name'],
            'voter_srno': ['voter srno', 'voter_srno', 'voter serial', 'voter_serial', 'votersrno', 'serial no', 'serial_no'],
            'age': ['age'],
            'gender': ['gender'],
            'voting_card_no': ['voting card no.', 'voting card no', 'voting_card_no', 'votingcardno', 'voting card', 'card no'],
            'karyakarta': ['karyakarta', 'karyakarta']
        }
        
        # Find matching columns
        used_columns = set()
        for field, keywords in field_keywords.items():
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in keywords or any(keyword in col_lower for keyword in keywords):
                    if col not in used_columns:
                        column_mapping[col] = field
                        used_columns.add(col)
                        break
        
        # Rename columns based on mapping
        renamed_df = df.rename(columns=column_mapping)
        
        # Process each row
        voters_data = []
        for index, row in renamed_df.iterrows():
            # Extract data - no validation, accept any data
            # Only use actual voter ID from Excel, don't generate one
            voter_id_val = row.get('voter_id')
            if voter_id_val is None or pd.isna(voter_id_val) or str(voter_id_val).strip() == '':
                raise ValueError(f'Voter ID is missing in row {index + 1}. All voters must have a valid ID.')
            voter_data = {
                'voter_id': str(voter_id_val).strip(),
                'booth_no': None,
                'first_name': str(row.get('first_name', '')).strip() if pd.notna(row.get('first_name', '')) else '',
                'father_name': str(row.get('father_name', '')).strip() if pd.notna(row.get('father_name', '')) else '',
                'surname': str(row.get('surname', '')).strip() if pd.notna(row.get('surname', '')) else '',
                'full_name': str(row.get('full_name', '')).strip() if pd.notna(row.get('full_name', '')) else '',
                'mobile_no': str(row.get('mobile_no', '')).strip() if pd.notna(row.get('mobile_no', '')) else '',
                'yadibhag_no': str(row.get('yadibhag_no', '')).strip() if pd.notna(row.get('yadibhag_no', '')) else '',
                'yadibhag_name': str(row.get('yadibhag_name', '')).strip() if pd.notna(row.get('yadibhag_name', '')) else '',
                'voter_srno': str(row.get('voter_srno', '')).strip() if pd.notna(row.get('voter_srno', '')) else '',
                'age': None,
                'gender': str(row.get('gender', '')).strip() if pd.notna(row.get('gender', '')) else '',
                'voting_card_no': str(row.get('voting_card_no', '')).strip() if pd.notna(row.get('voting_card_no', '')) else '',
                'karyakarta': str(row.get('karyakarta', '')).strip() if pd.notna(row.get('karyakarta', '')) else ''
            }
            
            # Extract age if available
            age_val = row.get('age')
            if age_val is not None and pd.notna(age_val):
                try:
                    voter_data['age'] = int(age_val)
                except (ValueError, TypeError):
                    # If age is not numeric, ignore it
                    pass
            
            # Extract booth number if available and is numeric
            booth_val = row.get('booth_no')
            if booth_val is not None and pd.notna(booth_val):
                try:
                    voter_data['booth_no'] = int(booth_val)
                except (ValueError, TypeError):
                    # If booth number is not numeric, ignore it
                    pass
            
            # Extract specific data from other columns if not already mapped
            # Look for name-related fields
            if not voter_data['first_name']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    # Only use EnglishName or first name columns, not general 'name' which may contain booth names
                    if col_lower in ['englishname', 'english_name', 'first', 'first_name', 'first name'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            val_str = str(val).strip()
                            # Skip if it looks like a booth name or yadibhag name
                            if not any(indicator in val_str.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                                voter_data['first_name'] = val_str
                                break
            
            # Look for father name/middle name
            if not voter_data['father_name']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['middle', 'father name', 'father', 'middle name', 'middle_name', 'father_name'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            val_str = str(val).strip()
                            # Skip if it looks like a booth name or yadibhag name
                            if not any(indicator in val_str.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                                voter_data['father_name'] = val_str
                                break
            
            # Look for surname/last name
            if not voter_data['surname']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['last name', 'surname', 'last', 'last_name', 'last_name'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            val_str = str(val).strip()
                            # Skip if it looks like a booth name or yadibhag name
                            if not any(indicator in val_str.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                                voter_data['surname'] = val_str
                                break
            
            # Look for full name
            if not voter_data['full_name']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    # Only look for actual full name fields, not general 'name' which might contain booth names
                    # Exclude 'name' column which often contains booth names in voter data
                    if col_lower in ['full name', 'fullname', 'full_name'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            val_str = str(val).strip()
                            # Skip if it looks like a booth name or yadibhag name
                            if not any(indicator in val_str.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                                voter_data['full_name'] = val_str
                                break
            
            # Look for mobile number
            if not voter_data['mobile_no']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['mobile no.', 'mobile number', 'phone', 'mobile', 'phone number', 'mobile_no.', 'mobile no'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            voter_data['mobile_no'] = str(val).strip()
                            break
            
            # Look for yadibhag number
            if not voter_data['yadibhag_no']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['yadibhag no', 'yadibhag_no', 'yadibhag no.', 'yadibhag'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            voter_data['yadibhag_no'] = str(val).strip()
                            break
            
            # Look for yadibhag name
            if not voter_data['yadibhag_name']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['yadibhag name', 'yadibhag_name', 'yadibhag name'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            val_str = str(val).strip()
                            # Skip if it looks like a booth name
                            if not any(indicator in val_str.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                                # Only set yadibhag_name if it's not already set as full_name
                                if not voter_data['full_name'] or voter_data['full_name'] == '':
                                    # Don't set yadibhag name as full name
                                    pass
                                voter_data['yadibhag_name'] = val_str
                                break
            
            # Look for voter serial number
            if not voter_data['voter_srno']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['voter srno', 'voter_srno', 'voter serial', 'voter_serial'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            voter_data['voter_srno'] = str(val).strip()
                            break
            
            # Look for age
            if voter_data['age'] is None:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['age'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            try:
                                voter_data['age'] = int(val)
                                break
                            except (ValueError, TypeError):
                                pass
            
            # Look for gender
            if not voter_data['gender']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['gender'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            voter_data['gender'] = str(val).strip()
                            break
            
            # Look for voting card number
            if not voter_data['voting_card_no']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['voting card no.', 'voting card no', 'voting_card_no', 'voting card', 'card no', 'card_no'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            voter_data['voting_card_no'] = str(val).strip()
                            break
            
            # Look for full name (constructed from other name fields if no explicit full name field exists)
            if not voter_data['full_name']:
                # Try to construct full name from first, middle, and last name
                first_name = voter_data.get('first_name', '')
                father_name = voter_data.get('father_name', '')  # Using middle name as father name
                surname = voter_data.get('surname', '')
                
                full_name_parts = []
                if first_name and not any(indicator in first_name.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                    full_name_parts.append(first_name)
                if father_name and not any(indicator in father_name.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                    full_name_parts.append(father_name)
                if surname and not any(indicator in surname.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not', 'yadibhag', 'yadi', 'bhag', ':', 'टेल्को', 'कपूर', 'से.क्र', 'सेन्ट', 'उर्सल', 'स्कुल', 'लोकम', 'टेतको', 'कपूर']):
                    full_name_parts.append(surname)
                
                if full_name_parts:
                    voter_data['full_name'] = ' '.join(full_name_parts)
            
            # Look for karyakarta
            if not voter_data['karyakarta']:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in ['karyakarta'] and col not in column_mapping:
                        val = row.get(col)
                        if val is not None and pd.notna(val):
                            voter_data['karyakarta'] = str(val).strip()
                            break
            
            # Try to extract booth number from any column if not already set
            if voter_data['booth_no'] is None:
                for col in df.columns:
                    col_lower = col.lower().strip()
                    # Check for booth-related column names that might not have been mapped
                    if any(keyword in col_lower for keyword in ['booth no.', 'booth_no', 'booth no', 'boothno', 'booth no.', 'booth_no.', 'booth']) and col not in column_mapping:
                        booth_val = row.get(col)
                        if booth_val is not None and pd.notna(booth_val):
                            try:
                                voter_data['booth_no'] = int(booth_val)
                                break
                            except (ValueError, TypeError):
                                pass
            
            voters_data.append(voter_data)
        
        return voters_data
        
    except Exception as e:
        raise e


@voter_bp.route('/')
@login_required
def index():
    return redirect(url_for('voter.search'))


@voter_bp.route('/search')
@login_required
def search():
    # Get all search parameters
    query = request.args.get('query', '')
    voter_id = request.args.get('voter_id', '')
    full_name = request.args.get('full_name', '')
    booth_no = request.args.get('booth_no', '')
    mobile_no = request.args.get('mobile_no', '')
    yadibhag_no = request.args.get('yadibhag_no', '')
    yadibhag_name = request.args.get('yadibhag_name', '')
    voter_srno = request.args.get('voter_srno', '')
    age = request.args.get('age', '')
    gender = request.args.get('gender', '')
    voting_card_no = request.args.get('voting_card_no', '')
    karyakarta = request.args.get('karyakarta', '')
    
    # Build search query
    search_query = Voter.query
    
    # Check if any search parameter is provided
    if any([query, voter_id, full_name, booth_no, mobile_no, voting_card_no, yadibhag_no, yadibhag_name, voter_srno, age, gender, karyakarta]):
        # Create a list of OR conditions
        or_conditions = []
        
        # Add individual field filters if provided
        if voter_id:
            # For voter_id, use exact match
            or_conditions.append(Voter.voter_id == voter_id)
        if full_name:
            or_conditions.append(Voter.full_name.ilike(f'%{full_name}%'))
        if mobile_no:
            or_conditions.append(Voter.mobile_no.ilike(f'%{mobile_no}%'))
        if booth_no:
            try:
                booth_no_int = int(booth_no)
                or_conditions.append(Voter.booth_no == booth_no_int)
            except ValueError:
                flash('Invalid booth number', 'error')
                # Return empty results if booth number is invalid
                voters = []
                return render_template('voter/search.html', voters=voters)
        if yadibhag_no:
            or_conditions.append(Voter.yadibhag_no.ilike(f'%{yadibhag_no}%'))
        if yadibhag_name:
            or_conditions.append(Voter.yadibhag_name.ilike(f'%{yadibhag_name}%'))
        if voter_srno:
            or_conditions.append(Voter.voter_srno.ilike(f'%{voter_srno}%'))
        if age:
            try:
                age_int = int(age)
                or_conditions.append(Voter.age == age_int)
            except ValueError:
                flash('Invalid age', 'error')
                # Return empty results if age is invalid
                voters = []
                return render_template('voter/search.html', voters=voters)
        if gender:
            or_conditions.append(Voter.gender.ilike(f'%{gender}%'))
        if voting_card_no:
            # For voting card number, use exact match
            or_conditions.append(Voter.voting_card_no == voting_card_no)
        if karyakarta:
            or_conditions.append(Voter.karyakarta.ilike(f'%{karyakarta}%'))
        
        # Apply general query filter (searches all fields) if provided
        if query:
            general_conditions = db.or_(
                Voter.voter_id.ilike(f'%{query}%'),
                Voter.full_name.ilike(f'%{query}%'),
                Voter.mobile_no.ilike(f'%{query}%'),
                Voter.yadibhag_no.ilike(f'%{query}%'),
                Voter.yadibhag_name.ilike(f'%{query}%'),
                Voter.voter_srno.ilike(f'%{query}%'),
                Voter.karyakarta.ilike(f'%{query}%')
            )
            # If both specific and general filters exist, combine them with OR
            if or_conditions:
                or_conditions.append(general_conditions)
                search_query = search_query.filter(db.or_(*or_conditions))
            else:
                # Only general query provided
                search_query = search_query.filter(general_conditions)
        elif or_conditions:
            # Only specific filters provided
            search_query = search_query.filter(db.or_(*or_conditions))
    
    voters = search_query.order_by(Voter.full_name).limit(100).all()  # Limit results for performance
    
    # If request is AJAX, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        voters_data = []
        for voter in voters:
            voters_data.append({
                'id': voter.id,
                'voter_id': voter.voter_id,
                'first_name': voter.first_name,
                'father_name': voter.father_name,
                'surname': voter.surname,
                'full_name': voter.full_name,
                'booth_no': voter.booth_no,
                'mobile_no': voter.mobile_no,
                'yadibhag_no': voter.yadibhag_no,
                'yadibhag_name': voter.yadibhag_name,
                'voter_srno': voter.voter_srno,
                'age': voter.age,
                'gender': voter.gender,
                'voting_card_no': voter.voting_card_no,
                'karyakarta': voter.karyakarta,
                'star_display': voter.get_star_display(),
                'star_rating': voter.star_rating
            })
        return jsonify({'voters': voters_data})
    
    return render_template('voter/search.html', voters=voters)


@voter_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_excel():
    # Only main user can upload files
    if current_user.role != 'main':
        flash('Only main user can upload Excel files', 'error')
        return redirect(url_for('voter.search'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Save file temporarily
                filename = secure_filename(file.filename)
                temp_path = os.path.join('temp', filename)
                
                # Create temp directory if it doesn't exist
                os.makedirs('temp', exist_ok=True)
                
                file.save(temp_path)
                
                # Process the Excel file
                voters_data = process_excel_file(temp_path)
                
                # Check for duplicates before inserting
                new_voters = []
                skipped_count = 0
                
                for voter_data in voters_data:
                    existing_voter = Voter.query.filter_by(voter_id=voter_data['voter_id']).first()
                    if existing_voter:
                        # Skip duplicate voter
                        skipped_count += 1
                    else:
                        # Create new voter
                        new_voter = Voter(
                            voter_id=voter_data['voter_id'],
                            booth_no=voter_data['booth_no'],
                            first_name=voter_data['first_name'],
                            father_name=voter_data['father_name'],
                            surname=voter_data['surname'],
                            full_name=voter_data['full_name'],
                            mobile_no=voter_data['mobile_no'],
                            yadibhag_no=voter_data['yadibhag_no'],
                            yadibhag_name=voter_data['yadibhag_name'],
                            voter_srno=voter_data['voter_srno'],
                            age=voter_data['age'],
                            gender=voter_data['gender'],
                            voting_card_no=voter_data['voting_card_no'],
                            karyakarta=voter_data['karyakarta']
                        )
                        new_voters.append(new_voter)
                
                # Bulk insert new voters
                for voter in new_voters:
                    db.session.add(voter)
                
                db.session.commit()
                
                # Clean up temp file
                os.remove(temp_path)
                
                success_count = len(new_voters)
                flash(f'Upload successful! Added {success_count} new voters', 'success')
                if skipped_count > 0:
                    flash(f'Skipped {skipped_count} duplicate voters', 'info')
                
                return redirect(url_for('voter.search'))
                
            except ValueError as ve:
                flash(f'Invalid data in Excel file: {str(ve)}', 'error')
            except Exception as e:
                flash(f'Error processing Excel file: {str(e)}', 'error')
        else:
            flash('Invalid file type. Please upload .xlsx or .xls files', 'error')
    
    return render_template('voter/upload.html')


@voter_bp.route('/preview_excel', methods=['POST'])
@login_required
def preview_excel():
    # Only main user can preview Excel files
    if current_user.role != 'main':
        return jsonify({'success': False, 'message': 'Only main user can preview Excel files'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            temp_path = os.path.join('temp', filename)
            
            # Create temp directory if it doesn't exist
            os.makedirs('temp', exist_ok=True)
            
            file.save(temp_path)
            
            # Read Excel file to preview
            df = pd.read_excel(temp_path)
            
            # Check if voter ID column exists
            voter_id_column_found = False
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(keyword in col_lower for keyword in ['voter', 'id', 'voterid', 'voter_id', 'voter id', 'srno', 'voter srno', 'voter_srno', 'votersrno', 'voting card no', 'voting card no.', 'voting_card_no']):
                    voter_id_column_found = True
                    break
            
            if not voter_id_column_found:
                os.remove(temp_path)
                return jsonify({'success': False, 'message': 'No Voter ID column found in Excel file. Please include a column with voter identification (e.g., voter_id, srno, voting card no, etc.)'}), 400
            
            # Get first 10 rows for preview
            preview_data = df.head(10).to_dict('records')
            
            # Get all column names
            columns = list(df.columns)
            
            # Remove temp file
            os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'columns': columns,
                'preview_data': preview_data,
                'total_rows': len(df)
            })
        
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error reading Excel file: {str(e)}'}), 500
    
    return jsonify({'success': False, 'message': 'Invalid file type. Please upload .xlsx or .xls files'}), 400


@voter_bp.route('/star/<int:voter_id>', methods=['POST'])
@login_required
def star_voter(voter_id):
    voter = Voter.query.get_or_404(voter_id)
    
    # Get the star rating from the request
    rating = request.json.get('rating', 1) if request.is_json else request.form.get('rating', 1)
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid rating value'}), 400
    
    # Store old rating for audit log
    old_rating = voter.star_rating
    
    # Update voter rating
    voter.star_rating = rating
    db.session.commit()
    
    # Create audit log
    star_log = StarLog(
        voter_id=voter.id,
        user_id=current_user.id,
        action='ADD' if old_rating == 0 else 'EDIT',
        old_rating=old_rating,
        new_rating=rating
    )
    db.session.add(star_log)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Star rating updated successfully',
        'star_display': voter.get_star_display(),
        'rating': voter.star_rating
    })


@voter_bp.route('/unstar/<int:voter_id>', methods=['POST'])
@login_required
def unstar_voter(voter_id):
    voter = Voter.query.get_or_404(voter_id)
    
    # Only main user can remove star ratings
    if current_user.role != 'main':
        return jsonify({'success': False, 'message': 'Only main user can remove star ratings'}), 403
    
    # Store old rating for audit log
    old_rating = voter.star_rating
    
    # Remove star rating
    voter.star_rating = 0
    db.session.commit()
    
    # Create audit log
    star_log = StarLog(
        voter_id=voter.id,
        user_id=current_user.id,
        action='DELETE',
        old_rating=old_rating,
        new_rating=0
    )
    db.session.add(star_log)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Star rating removed successfully',
        'star_display': '',
        'rating': 0
    })


@voter_bp.route('/voter/<int:voter_id>')
@login_required
def voter_detail(voter_id):
    voter = Voter.query.get_or_404(voter_id)
    return render_template('voter/detail.html', voter=voter)


@voter_bp.route('/clear_data', methods=['POST'])
@login_required
def clear_data():
    # Only main user can clear data
    if current_user.role != 'main':
        flash('Only main user can clear data', 'error')
        return redirect(url_for('voter.search'))
    
    try:
        # Delete all voter records
        deleted_count = db.session.query(Voter).delete()
        db.session.commit()
        
        flash(f'Successfully deleted {deleted_count} voter records from database', 'success')
        return redirect(url_for('voter.search'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing data: {str(e)}', 'error')
        return redirect(url_for('voter.search'))