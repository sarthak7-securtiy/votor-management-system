"""
Script to analyze the Excel file structure and data
"""
import pandas as pd
import os

def analyze_excel():
    # Path to the Excel file
    file_path = os.path.join(os.getcwd(), 'temp', 'Alphabeticalwise_Report_2026-01-02.xlsx')
    
    if not os.path.exists(file_path):
        print(f"❌ Excel file not found at: {file_path}")
        return False
    
    print(f"✓ Excel file found: {file_path}")
    
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        print(f"File has {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Show first few rows to understand the data
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Check for voter ID 38829 specifically
        print(f"\nLooking for voter ID 38829:")
        voter_row = df[df['SrNo'] == 38829]  # Assuming SrNo is the voter ID column
        if not voter_row.empty:
            print("Voter 38829 found:")
            for col, val in voter_row.iloc[0].items():
                print(f"  {col}: {val}")
        else:
            # Try different column names for voter ID
            for col in df.columns:
                if 'id' in col.lower() or 'srno' in col.lower():
                    voter_row = df[df[col] == 38829]
                    if not voter_row.empty:
                        print(f"Voter 38829 found in column '{col}':")
                        for col_name, val in voter_row.iloc[0].items():
                            print(f"  {col_name}: {val}")
                        break
            else:
                print("Voter 38829 not found in the dataset")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    analyze_excel()