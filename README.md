Relapse Detection using Autoencoder and Random Forest
This project implements an alert mechanism to detect relapse events in patients with bipolar disorder using physiological and activity data. The approach uses an autoencoder trained only on normal (label = 0) data to detect anomalies, followed by evaluation and interpretation of the alerts.

### Dataset
The dataset contains daily-level features from a single patient, including:

Heart rate statistics (e.g., hr_mean, hr_max)

Movement data (e.g., gyr_var, linacc_max)

Steps, calories, and sleep metrics

Date and label (0 = normal, 1 = relapse)

Relapse periods used for evaluation:

Severe episode: 2020-09-30 to 2020-10-29

Moderate episode: 2021-03-13 to 2021-03-18

The patient used is identified as 5031 (ID: 5f615ea99e38890013062039).

### Dataset Preparation
Before model implementation, we constructed a clean, feature-rich dataset from the raw .zip files. For simplicity and computational efficiency, we focused on a single patient. The dataset preparation involved the following steps, implemented through Python scripts in the code_for_preparing_dataset/ directory:

Initial Exploration
Using stats_output.py and tar_files_missing.py to assess file availability, date coverage, and missing data.

Label Assignment
The assign_labels.py script assigned labels to each zip file based on naming conventions and known relapse periods.

Feature Extraction and Dataset Construction
The create_final_dataset.py script extracted key metrics from each zip file and compiled them into a unified dataset.

Profiling and Quality Checks
The y_profiler.py script profiled the generated dataset and helped identify inconsistencies and missing values.

Data Cleaning and Feature Engineering
The data_preprocessing.py script cleaned the dataset by removing or imputing missing values and engineering additional features and flags.

The final dataset produced from this process was used as input for the modeling notebook.

### Methodology
1. Autoencoder Training
Trained exclusively on normal days (label = 0)

Reconstruction loss was calculated for the test data

Alerts were triggered when reconstruction loss exceeded the 95th percentile of the normal data

2. Alert Evaluation
Alerts were compared against known relapse dates

Evaluation metrics included:

Precision, Recall, F1 Score

ROC AUC

Confusion Matrix

The specific dates on which alerts were triggered were also listed

3. Explanation of Alerts
For each alert, especially those occurring outside of the relapse periods, the top features contributing to the reconstruction loss were identified and reported

Results Summary
Approximately 24% of days triggered anomaly alerts

The model identified 10 relapse days

ROC AUC for reconstruction loss was approximately 0.52, indicating weak separation

Alerts were analyzed by label and explained based on feature contributions

### Limitations and Future Work
Reconstruction loss alone is a weak predictor of relapse (low AUC)

The choice of threshold significantly affects precision and recall

The Random Forest classifier did not provide strong improvement, likely due to limited sample size and class imbalance

Future improvements may include:

Incorporating time-series models such as LSTM or Transformers

Using a variational autoencoder

Engineering temporal or behavioral features

