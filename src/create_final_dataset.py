import os
import tarfile
import pandas as pd
import numpy as np
from collections import defaultdict
import time
from multiprocessing import Pool, cpu_count

def load_tar_contents(tar_path):
    data = {}
    with tarfile.open(tar_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                name = os.path.basename(member.name).lower()
                f = tar.extractfile(member)
                if f:
                    try:
                        df = pd.read_csv(f, header=0, sep=None, engine='python', on_bad_lines='skip')
                        for col in df.columns:
                            df[col] = df[col].apply(lambda x: str(x).replace(',', '.') if isinstance(x, str) else x)
                        df = df.apply(lambda col: pd.to_numeric(col, errors='coerce') if col.dtype == object else col)
                        data[name] = df.reset_index(drop=True)
                    except Exception as e:
                        print(f" Failed to read {name}: {e}")
    return data

def aggregate_sensor_data(contents_list):
    features = {}

    combined = defaultdict(list)
    for content in contents_list:
        for key, df in content.items():
            combined[key].append(df)
    combined = {k: pd.concat(v, ignore_index=True) for k, v in combined.items()}

    # HRM
    if "hrm" in combined:
        df = combined["hrm"]
        if "heartRate" in df.columns:
            df = df[pd.to_numeric(df["heartRate"], errors="coerce").notnull()]
            df = df[df["heartRate"] >= 0]
            df["heartRate"] = df["heartRate"].astype(float)
            if not df.empty:
                features["hr_mean"] = round(df["heartRate"].mean(), 3)
                features["hr_min"] = round(df["heartRate"].min(), 3)
                features["hr_max"] = round(df["heartRate"].max(), 3)
                features["hr_median"] = round(df["heartRate"].median(), 3)
                features["hr_valid_count"] = len(df)

    # GYR
    if "gyr" in combined:
        df = combined["gyr"]
        if set(["X", "Y", "Z"]).issubset(df.columns):
            df = df[["X", "Y", "Z"]].apply(lambda col: col.astype(str).str.replace(",", ".").astype(float))
            magnitude = np.sqrt(df["X"]**2 + df["Y"]**2 + df["Z"]**2)
            features["gyr_var"] = round(df.var().sum(), 3)
            features["gyr_max"] = round(magnitude.max(), 3)
            features["gyr_energy"] = round((magnitude**2).sum(), 3)

    # LINACC
    if "linacc" in combined:
        df = combined["linacc"]
        if set(["X", "Y", "Z"]).issubset(df.columns):
            df = df[["X", "Y", "Z"]].apply(lambda col: pd.to_numeric(col.astype(str).str.replace(",", "."), errors='coerce'))
            magnitude = np.sqrt(df["X"]**2 + df["Y"]**2 + df["Z"]**2)
            features["linacc_var"] = round(df.var().sum(), 3)
            features["linacc_max"] = round(magnitude.max(), 3)
            features["linacc_energy"] = round((magnitude**2).sum(), 3)

    # STEP
    if "step" in combined:
        df = combined["step"]
        required_cols = {"stepsWalking", "stepsRunning", "distance", "calories"}
        if required_cols.issubset(df.columns):
            df["distance"] = df["distance"].astype(str).str.replace(",", ".").astype(float)
            df["calories"] = df["calories"].astype(str).str.replace(",", ".").astype(float)
            features["steps_walking"] = df["stepsWalking"].sum()
            features["steps_running"] = df["stepsRunning"].sum()
            features["total_distance"] = round(df["distance"].sum(), 3)
            features["total_calories"] = round(df["calories"].sum(), 3)

    # SLEEP
    if "sleep" in combined:
        df = combined["sleep"]
        if set(["sleeping", "duration"]).issubset(df.columns):
            df["duration"] = df["duration"].astype(str).str.replace(",", ".").astype(float)
            df["sleeping"] = df["sleeping"].astype(float)
            total_duration = df["duration"].sum()
            sleep_duration = df[df["sleeping"] == 1]["duration"].sum()
            features["sleep_ratio"] = round(sleep_duration / total_duration, 3) if total_duration > 0 else 0

    return features

def process_all_dates(tar_dir, label_csv_path, output_csv_path):
    date_tar_map = defaultdict(list)
    for fname in os.listdir(tar_dir):
        if fname.endswith(".tar.gz"):
            try:
                date_part = fname.split("_")[1].split("T")[0]
                date_tar_map[date_part].append(os.path.join(tar_dir, fname))
            except Exception:
                continue

    labels_df = pd.read_csv(label_csv_path)
    label_map = dict(zip(labels_df["date"], labels_df["label"]))

    results = []
    for date, tar_paths in sorted(date_tar_map.items()):
        print(f" Processing date {date} ({len(tar_paths)} file(s))")
        contents_list = [load_tar_contents(path) for path in tar_paths]

        # with Pool(processes=cpu_count()) as pool:
        #     contents_list = pool.map(load_tar_contents, tar_paths)

        features = aggregate_sensor_data(contents_list)
        features["date"] = date
        features["label"] = label_map.get(date, None)
        results.append(features)
        print(f" Done: {date} → Label: {features['label']} | Files: {len(tar_paths)}")

    df = pd.DataFrame(results)
    df.to_csv(output_csv_path, index=False)
    print(f"\n Saved all daily features to: {output_csv_path}")

# def process_all_dates(tar_dir, label_csv_path, output_csv_path):
#     tar_files = []
#     date_parts = []

#     for fname in os.listdir(tar_dir):
#         if fname.endswith(".tar.gz"):
#             try:
#                 date_part = fname.split("_")[1].split("T")[0]
#                 full_path = os.path.join(tar_dir, fname)
#                 tar_files.append(full_path)
#                 date_parts.append(date_part)
#             except Exception:
#                 continue

#     # Parallel loading of all .tar.gz files
#     print(f" Loading {len(tar_files)} tar files using {cpu_count()} processes...")
#     with Pool(processes=cpu_count()) as pool:
#         all_contents = pool.map(load_tar_contents, tar_files)

#     # Group contents by date
#     grouped_by_date = defaultdict(list)
#     for date, contents in zip(date_parts, all_contents):
#         grouped_by_date[date].append(contents)

#     labels_df = pd.read_csv(label_csv_path)
#     label_map = dict(zip(labels_df["date"], labels_df["label"]))

#     results = []
#     for date, contents_list in sorted(grouped_by_date.items()):
#         print(f" Processing date: {date} with {len(contents_list)} file(s)")
#         features = aggregate_sensor_data(contents_list)
#         features["date"] = date
#         features["label"] = label_map.get(date, None)
#         results.append(features)
#         print(f" Done: {date} → Label: {features['label']} | Files: {len(contents_list)}")

#     df = pd.DataFrame(results)
#     df.to_csv(output_csv_path, index=False)
#     print(f"\n Saved all daily features to: {output_csv_path}")


# Example usage
if __name__ == "__main__":
    start_time = time.time()
    process_all_dates(
        tar_dir=r"C:\Users\menyc\Downloads\hash test\selected\5f615ea99e38890013062039",
        label_csv_path=r"C:\Users\menyc\Downloads\hash test\selected\labeled_dataset.csv",
        output_csv_path=r"C:\Users\menyc\Downloads\hash test\selected\daily_features_final.csv"
    )
    end_time = time.time()
    print(f"Total time the process took is {(end_time - start_time)/60:.2f} minutes")

