import pandas as pd
import sys
import time

start_time = time.time()
file_path = "Study Case for Univ Airlangga 2026 _Actuarial AXA.xlsx"

with open("output_explore.txt", "w", encoding="utf-8") as f:
    try:
        f.write("Starting analysis...\n")
        excel_data = pd.ExcelFile(file_path)
        f.write(f"Sheets found: {excel_data.sheet_names}\n")
        
        for sheet in excel_data.sheet_names:
            f.write(f"\n--- Sheet: {sheet} ---\n")
            df = pd.read_excel(file_path, sheet_name=sheet)
            f.write(f"Columns: {df.columns.tolist()}\n")
            f.write(f"Shape: {df.shape}\n")
            f.write("\nFirst 3 rows:\n")
            f.write(df.head(3).to_string())
            f.write("\n")
            
        f.write(f"\nCompleted in {time.time() - start_time:.2f} seconds\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
