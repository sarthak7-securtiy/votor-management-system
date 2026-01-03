"""
Script to check the Excel file structure and how it's being mapped
"""
import pandas as pd
import os

def check_excel_mapping():
    # Check if temp directory has any Excel files
    temp_dir = os.path.join(os.getcwd(), 'temp')
    excel_files = [f for f in os.listdir(temp_dir) if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print("No Excel files found in temp directory")
        return False
    
    file_path = os.path.join(temp_dir, excel_files[0])
    print(f"Analyzing Excel file: {file_path}")
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        print(f"File has {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
        
        # Show a few sample rows to understand the data structure
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Look for a row that might have the problematic data
        print("\nLooking for sample row with booth name pattern...")
        for idx, row in df.iterrows():
            for col, val in row.items():
                if pd.notna(val) and ('booth' in str(val).lower() or 'बूथ' in str(val) or 'जाहीर' in str(val)):
                    print(f"Row {idx}, Column '{col}': {val}")
                    break
            if idx >= 4:  # Just check first 5 rows
                break
        
        # Show the structure of a specific voter record
        if len(df) > 0:
            print(f"\nSample voter record (first row):")
            for col, val in df.iloc[0].items():
                print(f"  {col}: {val}")
        
        return True
        
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    check_excel_mapping()