# Data-Driven Drug Interaction and Severity Assessment Tool for Pediatric Adverse Drug Reactions Mitigation

* [Project Overview](#ovr)
* [Data Source](#erd)
* [Technologies Used](#tech)
* [Current Progress](#ip)
* [Methodology](#method)
	* [Data Preprocessing](#prep)
	* [Weight Imputation](#impute)
* [Usage](#using)
* [Accessing raw data](#access)

## <a name= "ovr"></a>Project Overview
Adverse drug reactions (ADRs) are a major concern in healthcare, especially in pediatric populations where polypharmacy is common. This project aims to develop a data-driven tool to assess drug-drug interaction (DDI) severity in pediatric patients for safer prescribing decisions.

### Objectives
* Identify and validate pediatric ADRs using FAERS data.
* Classify severity of each identified drug interaction as mild, moderate, or severe.
* Develop a real-time tool to support clinicians in safer prescribing.

### Stakeholders
* Healthcare professionals: Safer prescribing decisions.
* Patients: Reduced risk of ADRs.
* Pharmacovigilance researchers: Insights into drug interactions.
* Government & healthcare institutions: Improved monitoring & reporting.

## <a name= "erd"></a>Data Source
The project uses FAERS (FDA Adverse Event Reporting System) data from 2021 onwards (post-COVID) to ensure more accurate and relevant results. Data is cleaned and preprocessed for association rule mining and predictive modelling.


<img width="574" alt="Data-Source" src="https://github.com/user-attachments/assets/4e7a23d9-c8c7-4ec4-9b22-529c3744072e">

## <a name= "tech"></a>Technologies Used (So far)
* ETL Pipeline: Python (Pandas)
* Machine Learning (Regression-based Imputation) : Scikit-learn
* Data Visualization: Matplotlib, Seaborn
* Version Control: Git
* Auditing/ Quick Data Validation: MS Excel

## <a name= "ip"></a>Current Progress
✅ Data Exploration & Cleaning Completed

✅ Weight Imputation Model Trained & Deployed

✅ Preprocessing of Demographics Table

🔲 Preprocessing of Remaining FAERS Entities- Drugs, Reactions, Outcomes (In Progress)

🔲 Association Rule Mining (Upcoming)

🔲 Severity Classification Model (Upcoming)

🔲 Streamlit Dashboard Development (Upcoming)

## <a name= "method"></a>Methodology

### <a name= "prep"></a>Data Preprocessing
* Extracted only required columns from FAERS dataset.
* Filtered pediatric population records based on age.
* Converted all age units to years and classified into age bins.
* Removed outliers (e.g., unrealistic ages, unknown genders).
* Created a unified 'origin country' feature from FAERS records

### <a name= "impute"></a>Weight Imputation
* Issue: Over 70% of weight values missing.
* Solution: Machine Learning-based Imputation
* Trained three models: Random Forest, Gradient Boosting, XGBoost.
* Evaluation Metrics: R² Score, RMSE, MAE, MAPE.
* Final Model: Random Forest (Preserves data distribution).

## <a name= "using"></a>Usage

### Clone the repository
```
git clone https://github.com/kisaraF/Pediatric-ADR-DDI-Tool.git
cd Pediatric-ADR-DDI-Tool
```

### Running Scripts
First add the raw data into `Data/RAW_DATA/DEMOGRAPHICS`

Then head to 
```
cd Scripts/Demographic\ Scripts 
```

#### Apply Transformations
```
python Transform_Script_demog.py
```

#### Combine transformed data and remove duplicates
```
python combine_transformed_files_demog.py
```

#### Use the regression-based imputation model to predict missing values
```
python predict_missing_values_demog.py
```

## <a name= "access"></a>Accessing Raw Data
* FDA quarterly publications – <a href='https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html'>link</a>
* Quick access (saves hassle of unzipping and selecting each file) - <a href='https://drive.google.com/drive/folders/1g561wpNAcK3QvFaqeqVWhvjjKbEaoZU3?usp=drive_link'>link</a>
