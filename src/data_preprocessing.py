import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def clean_hr_valid_count(df):
    median_valid_count = df.loc[df["hr_valid_count"] != 0, "hr_valid_count"].median()
    condition_preserve = (df["label"] == 1) & (df["hr_valid_count"] == 0)
    df.loc[condition_preserve, "hr_valid_count"] = median_valid_count

    condition_drop = (df["label"] == 0) & (df["hr_valid_count"] == 0)
    label_counts_before = df.loc[condition_drop, "label"].value_counts()

    initial_rows = df.shape[0]
    df = df[~condition_drop]
    final_rows = df.shape[0]

    return df

def impute_with_normal_distribution(df, column, seed=42, clip_percentiles=(0.05, 0.95)):
    df[f"{column}_was_zero"] = df[column] == 0

    df[column] = df[column].replace(0, np.nan)
    valid_data = df[column].dropna()

    mean = valid_data.mean()
    std = valid_data.std()
    num_missing = df[column].isna().sum()

    np.random.seed(seed)
    synthetic_values = np.random.normal(loc=mean, scale=std, size=num_missing)

    lower = valid_data.quantile(clip_percentiles[0])
    upper = valid_data.quantile(clip_percentiles[1])
    synthetic_values = np.clip(synthetic_values, lower, upper)

    df.loc[df[column].isna(), column] = synthetic_values

    return df

# File paths
input_path = "daily_features_final.csv"
output_path = "daily_features_cleaned.csv"

# Load dataset
df = pd.read_csv(input_path)

# HR columns
for col in ["hr_mean", "hr_min", "hr_max", "hr_median"]:
    df[f"{col}_was_zero"] = df[col] == 0
    df[col] = df[col].replace(0, np.nan)
    if col == "hr_max":
        df[col] = np.where(df[col] > 216, 216, df[col])
    df[col].fillna(df[col].median(), inplace=True)

# Clean hr_valid_count
df = clean_hr_valid_count(df)

# GYR columns
df["gyr_var_was_zero"] = df["gyr_var"] == 0
df["gyr_var"] = df["gyr_var"].replace(0, np.nan)
df["gyr_var"].fillna(df["gyr_var"].median(), inplace=True)

df = impute_with_normal_distribution(df, column="gyr_max")

df["gyr_energy_was_zero"] = df["gyr_energy"] == 0
df["gyr_energy"] = df["gyr_energy"].replace(0, np.nan)
df["gyr_energy"].fillna(df["gyr_energy"].median(), inplace=True)

# LINACC columns
for col in ["linacc_var", "linacc_max", "linacc_energy"]:
    df[f"{col}_was_zero"] = df[col] == 0
    df[col] = df[col].replace(0, np.nan)
    df[col].fillna(df[col].median(), inplace=True)

# STEPS columns
steps_cols = ["steps_walking", "steps_running", "total_distance", "total_calories"]

# Process each column with the same logic
for col in steps_cols:
    # Track whether the original value was invalid
    df[f"{col}_was_invalid"] = df[col] <= 0

    # Replace invalid values (≤ 0) with NaN
    df[col] = df[col].apply(lambda x: np.nan if x <= 0 else x)

    # Impute NaNs with the median of valid values
    median_val = df[col].median()
    df[col].fillna(median_val, inplace=True)

# Drop those rows
df_cleaned = df.drop(columns=["linacc_max_was_zero", "gyr_max_was_zero", "hr_min", "hr_valid_count"])

# Save cleaned dataset
df_cleaned.to_csv(output_path, index=False)
print(f" Cleaned dataset with cleaned columns saved to: {output_path}")
