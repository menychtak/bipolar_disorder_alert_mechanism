import pandas as pd
import os

# Path to the CSV file in the same folder as this script
csv_path = os.path.join(os.path.dirname(__file__), 'labeled_dataset.csv')

# Read the CSV file
df = pd.read_csv(csv_path)

# Assume the date column is named 'date' and label column is 'label'
# Adjust these names if your CSV uses different column names
date_col = 'date'
label_col = 'label'

# Convert the date column to datetime
df[date_col] = pd.to_datetime(df[date_col])

# Find overall min and max date
min_date = df[date_col].min()
max_date = df[date_col].max()

print(f"Overall min date: {min_date}")
print(f"Overall max date: {max_date}")

# Number of dates with each label
label_counts = df[label_col].value_counts()
print("\nNumber of dates with each label:")
print(label_counts)

# Min and max date for each label
print("\nMin and max date for each label:")
for label, group in df.groupby(label_col):
    label_min = group[date_col].min()
    label_max = group[date_col].max()
    print(f"Label: {label} | Min date: {label_min} | Max date: {label_max}")

    # Save the statistics to a text file
    output_path = os.path.join(os.path.dirname(__file__), 'statistics_output.txt')
    with open(output_path, 'w') as f:
        f.write(f"Overall min date: {min_date}\n")
        f.write(f"Overall max date: {max_date}\n\n")
        f.write("Number of dates with each label:\n")
        f.write(label_counts.to_string())
        f.write("\n\nMin and max date for each label:\n")
        for label, group in df.groupby(label_col):
            label_min = group[date_col].min()
            label_max = group[date_col].max()
            f.write(f"Label: {label} | Min date: {label_min} | Max date: {label_max}\n")
    print(f"\nStatistics saved to {output_path}")