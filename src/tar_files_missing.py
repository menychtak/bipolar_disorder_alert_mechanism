import os
import pandas as pd
from collections import defaultdict

def extract_date_from_filename(filename):
    try:
        return filename.split("_")[1].split("T")[0]
    except IndexError:
        return None

def find_missing_dates(tar_dir, label_csv_path):
    # 1. Get all dates with label == 1
    label_df = pd.read_csv(label_csv_path)
    relapse_dates = sorted(label_df[label_df["label"] == 1]["date"].unique())

    # 2. Scan folder
    all_files = os.listdir(tar_dir)
    total_files = len(all_files)
    tar_gz_files = [f for f in all_files if f.endswith(".tar.gz")]
    tar_dates = set()

    for fname in tar_gz_files:
        date = extract_date_from_filename(fname)
        if date:
            tar_dates.add(date)

    # 3. Find missing
    missing_dates = [d for d in relapse_dates if d not in tar_dates]

    # 4. Report
    print("\n Summary Report")
    print(f"Total label=1 entries         : {len(label_df[label_df['label'] == 1])}")
    print(f"Unique label=1 dates          : {len(relapse_dates)}")
    print(f" Total files in folder       : {total_files}")
    print(f"  Total .tar.gz files         : {len(tar_gz_files)}")
    print(f" Available .tar.gz dates     : {len(tar_dates)}")
    print(f" Missing unique dates        : {len(missing_dates)}\n")

    for d in missing_dates:
        print(f"    - {d}")

    return missing_dates

# --- Example usage ---
if __name__ == "__main__":
    tar_dir = r"C:\Users\menyc\Downloads\hash test\selected\5f615ea99e38890013062039"
    label_csv_path = r"C:\Users\menyc\Downloads\hash test\selected\labeled_dataset.csv"
    find_missing_dates(tar_dir, label_csv_path)
