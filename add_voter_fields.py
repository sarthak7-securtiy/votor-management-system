"""
Script to add new fields to the voter table to match Excel columns
"""
import os
import sqlite3

def add_voter_fields():
    print("Adding new fields to voter table...")
    
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
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(voters)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns based on Excel file
        new_columns = {
            'yadibhag_no': 'TEXT',
            'yadibhag_name': 'TEXT', 
            'voter_srno': 'TEXT',
            'age': 'INTEGER',
            'gender': 'TEXT',
            'voting_card_no': 'TEXT',
            'karyakarta': 'TEXT'
        }
        
        # Add new columns if they don't exist
        for col_name, col_type in new_columns.items():
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE voters ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Added column: {col_name} ({col_type})")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"Column {col_name} already exists")
                    else:
                        print(f"❌ Error adding column {col_name}: {str(e)}")
            else:
                print(f"Column {col_name} already exists")
        
        # Commit the changes
        conn.commit()
        conn.close()
        
        print("✅ New fields added successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error adding voter fields: {str(e)}")
        return False

if __name__ == "__main__":
    add_voter_fields()