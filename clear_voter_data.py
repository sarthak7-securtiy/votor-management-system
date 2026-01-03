"""
Script to clear all voter data from the database
"""
import os
import sqlite3

def clear_voter_data():
    print("Clearing all voter data from the database...")
    
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
        
        # Get count of existing records
        cursor.execute("SELECT COUNT(*) FROM voters")
        count = cursor.fetchone()[0]
        print(f"Current voter records: {count}")
        
        # Clear all voter records
        cursor.execute("DELETE FROM voters")
        
        # Also clear star logs related to voters
        cursor.execute("DELETE FROM star_logs")
        
        # Commit the changes
        conn.commit()
        
        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM voters")
        new_count = cursor.fetchone()[0]
        
        print(f"✅ Voter data cleared successfully!")
        print(f"Records remaining: {new_count}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error clearing voter data: {str(e)}")
        return False

if __name__ == "__main__":
    clear_voter_data()