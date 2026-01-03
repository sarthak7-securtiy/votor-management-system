"""
Script to check the specific voter data in the database
"""
import os
import sys
import sqlite3

def check_voter_data():
    print("Checking voter data for ID 32464...")
    
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
        
        # Check the specific voter record
        print("\nChecking voter ID 32464:")
        cursor.execute("SELECT * FROM voters WHERE voter_id = '32464'")
        voter = cursor.fetchone()
        
        if voter:
            # Get column names
            cursor.execute("PRAGMA table_info(voters)")
            columns = [column[1] for column in cursor.fetchall()]
            
            print("Voter record:")
            for i, col in enumerate(columns):
                print(f"  {col}: {voter[i]}")
        else:
            print("❌ Voter ID 32464 not found in the database")
            
            # Check for similar IDs
            cursor.execute("SELECT voter_id, first_name, surname FROM voters WHERE voter_id LIKE '%32464%' OR voter_id LIKE '3246%'")
            similar_voters = cursor.fetchall()
            
            if similar_voters:
                print("\nFound similar voter IDs:")
                for voter in similar_voters:
                    print(f"  ID: {voter[0]}, First Name: {voter[1]}, Surname: {voter[2]}")
            else:
                print("\nNo similar voter IDs found")
        
        # Check some sample records to understand the data structure
        print("\nSample voter records:")
        cursor.execute("SELECT voter_id, first_name, surname, full_name FROM voters LIMIT 5")
        sample_voters = cursor.fetchall()
        for voter in sample_voters:
            print(f"  ID: {voter[0]}, First: {voter[1]}, Surname: {voter[2]}, Full: {voter[3]}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error checking voter data: {str(e)}")
        return False

if __name__ == "__main__":
    check_voter_data()