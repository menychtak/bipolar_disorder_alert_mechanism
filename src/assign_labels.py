from datetime import datetime
import os
import csv
from collections import defaultdict

def is_relapse(file_date_str, relapse_periods):
    file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
    for start_str, end_str in relapse_periods:
        start = datetime.strptime(start_str, "%d/%m/%Y")
        end = datetime.strptime(end_str, "%d/%m/%Y")
        if start <= file_date <= end:
            return 1
    return 0

def extract_date_from_filename(filename):
    try:
        parts = filename.split('_')
        date_part = parts[1].split('T')[0]  # Extract YYYY-MM-DD
        return date_part
    except Exception as e:
        print(f"Error extracting date from filename: {filename} – {e}")
        return None

def main():
    # relapse_periods = [("30/09/2020", "29/10/2020"), ("13/03/2021", "18/03/2021")]
    relapse_periods = [("15/01/2020", "10/03/2020"), ("01/07/2020", "01/09/2020"), ("31/10/2020", "29/11/2020")]


    folder_path = r"C:\Users\menyc\Downloads\hash test\selected\5f615ea99e38890013062039"
    output_file = r"C:\Users\menyc\Downloads\hash test\selected\labeled_dataset.csv"

    files_by_date = defaultdict(list)

    # Group files by date
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".tar.gz"):
            date_part = extract_date_from_filename(filename)
            if date_part:
                files_by_date[date_part].append(filename)

    data_rows = []
    for date, files in files_by_date.items():
        label = is_relapse(date, relapse_periods)
        for filename in files:
            print(f"{filename} ➜ {date} ➜ label: {label}")
            data_rows.append([filename, date, label])

    # Save to CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "date", "label"])
        writer.writerows(data_rows)

    print(f"\n Saved labeled dataset to: {output_file}")

if __name__ == "__main__":
    main()
