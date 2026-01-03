"""
Script to fix the voter data by correcting booth names in name fields
"""
import os
import sqlite3

def fix_voter_data():
    print("Fixing voter data by correcting booth names in name fields...")
    
    # Database path
    db_path = os.path.join(os.getcwd(), 'app', 'instance', 'voter_management.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at: {db_path}")
        return False
    
    print(f"✓ Database file found: {db_path}")
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check how many records have booth names in the first_name field
        cursor.execute("SELECT COUNT(*) FROM voters WHERE first_name LIKE '%बूथ%' OR first_name LIKE '%booth%' OR first_name LIKE '%BOOTH%'")
        booth_name_count = cursor.fetchone()[0]
        print(f"Found {booth_name_count} records with booth names in first_name field")
        
        if booth_name_count > 0:
            # Get records with booth names in first_name field
            cursor.execute("SELECT id, voter_id, first_name FROM voters WHERE first_name LIKE '%बूथ%' OR first_name LIKE '%booth%' OR first_name LIKE '%BOOTH%'")
            records = cursor.fetchall()
            
            for record in records:
                voter_id, original_first_name = record[1], record[2]
                
                # Check if this looks like a booth name
                is_booth_name = any(indicator.lower() in original_first_name.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not'])
                
                if is_booth_name:
                    print(f"Fixing voter {voter_id}: '{original_first_name}' -> ''")
                    # Update the record to clear the first_name field (it will be properly set when data is reprocessed)
                    cursor.execute("UPDATE voters SET first_name = '' WHERE voter_id = ?", (voter_id,))
        
        # Also fix surname fields that might contain booth names
        cursor.execute("SELECT COUNT(*) FROM voters WHERE surname LIKE '%बूथ%' OR surname LIKE '%booth%' OR surname LIKE '%BOOTH%'")
        surname_booth_count = cursor.fetchone()[0]
        
        if surname_booth_count > 0:
            cursor.execute("SELECT id, voter_id, surname FROM voters WHERE surname LIKE '%बूथ%' OR surname LIKE '%booth%' OR surname LIKE '%BOOTH%'")
            records = cursor.fetchall()
            
            for record in records:
                voter_id, original_surname = record[1], record[2]
                
                is_booth_name = any(indicator.lower() in original_surname.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not'])
                
                if is_booth_name:
                    print(f"Fixing voter {voter_id} surname: '{original_surname}' -> ''")
                    cursor.execute("UPDATE voters SET surname = '' WHERE voter_id = ?", (voter_id,))
        
        # Also fix full_name fields that might contain booth names
        cursor.execute("SELECT COUNT(*) FROM voters WHERE full_name LIKE '%बूथ%' OR full_name LIKE '%booth%' OR full_name LIKE '%BOOTH%'")
        fullname_booth_count = cursor.fetchone()[0]
        
        if fullname_booth_count > 0:
            cursor.execute("SELECT id, voter_id, full_name FROM voters WHERE full_name LIKE '%बूथ%' OR full_name LIKE '%booth%' OR full_name LIKE '%BOOTH%'")
            records = cursor.fetchall()
            
            for record in records:
                voter_id, original_fullname = record[1], record[2]
                
                is_booth_name = any(indicator.lower() in original_fullname.lower() for indicator in ['booth', ' booth', 'बूथ', 'जाहीर', 'nahi', 'no', 'not'])
                
                if is_booth_name:
                    print(f"Fixing voter {voter_id} full_name: '{original_fullname}' -> ''")
                    cursor.execute("UPDATE voters SET full_name = '' WHERE voter_id = ?", (voter_id,))
        
        # Commit the changes
        conn.commit()
        
        # Count how many records were fixed
        cursor.execute("SELECT COUNT(*) FROM voters WHERE first_name LIKE '%बूथ%' OR first_name LIKE '%booth%' OR first_name LIKE '%BOOTH%'")
        remaining_booth_names = cursor.fetchone()[0]
        
        print(f"✅ Fixed voter data successfully!")
        print(f"Remaining records with booth names: {remaining_booth_names}")
        
        # Show a sample of corrected records
        print("\nSample of corrected records:")
        cursor.execute("SELECT voter_id, first_name, surname, full_name FROM voters WHERE voter_id IN ('32464', '57263', '22780', '36330', '22819') LIMIT 5")
        sample_voters = cursor.fetchall()
        for voter in sample_voters:
            print(f"  ID: {voter[0]}, First: '{voter[1]}', Surname: '{voter[2]}', Full: '{voter[3]}'")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error fixing voter data: {str(e)}")
        return False

if __name__ == "__main__":
    fix_voter_data()