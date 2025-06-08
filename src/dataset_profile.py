import pandas as pd
from ydata_profiling import ProfileReport

# Load data
df = pd.read_csv("daily_features_final.csv")

# Fill missing values
df.fillna(0, inplace=True)

# # TEMPORARY: Remove rows with extreme values in key columns
filtered_df = df[
    (df["gyr_var"] < 10000) & 
    (df["linacc_var"] < 50) & 
    (df["hr_mean"] < 200)
]
excluded_df = df[~(
    (df["gyr_var"] < 10000) &
    (df["linacc_var"] < 50) &
    (df["hr_mean"] < 200)
)]
print("Excluded rows summary:\n", excluded_df.describe())
print(excluded_df)

# Run profiling
profile = ProfileReport(
    filtered_df,
    title="Daily Features Report (Filtered)",
    correlations={"auto": {"calculate": False}},
)
profile.to_file("daily_features_report.html")
