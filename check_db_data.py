"""
Script to check what data is currently in the database
"""
import os
import sqlite3

def check_db_data():
    print("Checking current database data...")
    
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
        
        # Check how many records are in the database
        cursor.execute("SELECT COUNT(*) FROM voters")
        count = cursor.fetchone()[0]
        print(f"Total voters in database: {count}")
        
        if count > 0:
            # Check a sample of records to see what's stored
            cursor.execute("SELECT voter_id, first_name, full_name, yadibhag_name, booth_no FROM voters LIMIT 5")
            sample_records = cursor.fetchall()
            
            print("\nSample records from database:")
            for record in sample_records:
                print(f"  Voter ID: {record[0]}")
                print(f"    First Name: '{record[1]}'")
                print(f"    Full Name: '{record[2]}'")
                print(f"    Yadibhag Name: '{record[3]}'")
                print(f"    Booth No: {record[4]}")
                print()
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False

if __name__ == "__main__":
    check_db_data()