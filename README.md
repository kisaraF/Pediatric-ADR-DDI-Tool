# Data-Driven Drug Interaction and Severity Assessment Tool for Pediatric Adverse Drug Reactions Mitigation

* [Project Overview](#ovr)
* [Data Source](#erd)
* [Technologies Used](#tech)
* [Data Preprocessing](#method)
	* [Data Preprocessing (Demographics)](#demo-prep)
	* [Weight Imputation](#impute)
	* [Data Preprocessing (Drugs)](#drug-prep)
* [Modularized Data Preprocessing](#modular)
	* [Usage](#using)
* [Association Rule Mining](#assocr)
* [Outcome Severity Mining](#outc_sev)
* [Streamlit App](#dashboard)
* [Accessing raw data](#access)

## <a name= "ovr"></a>Project Overview
Adverse drug reactions (ADRs) are a major problem in pediatric healthcare with notable rates of morbidity and mortality with heavy economic burden. ADRs account for 16.9% of hospital admissions averaging the NHS £2.1 billion in costs annually. 

Polypharmacy and unique physiological features of children increase the likelihood of drug-drug interactions (DDIs). Therefore data-driven tools to support pharmacovigilance under clinical settings are much needed, which is the motive of this project.

### Aim 
This project aims to develop a data-driven tool for evaluating the severity of drug-drug interactions that could cause potential adverse drug reactions in pediatric patients to support clinicians to make safer prescribing decisions while elevating safety and quality of life of the patients.

### Objectives
* Identify and validate pediatric ADRs using post-COIVD FAERS data.
* Classify severity of each identified drug-drug interaction based on the "outcomes" data to understand potential impact on the patient.
* Developing a data-driven tool, supporting real-time assessment of DDIs along with the severity of outcomes. 
* Deploy the final version of the application to be easily accessible by the clinicians over the web.

### Stakeholders
* Healthcare professionals: Safer prescribing decisions.
* Patients: Reduced risk of ADRs.
* Pharmacovigilance researchers: Insights into drug interactions.
* Government & healthcare institutions: Improved monitoring & reporting.

## <a name= "erd"></a>Data Source
The project uses FAERS (FDA Adverse Event Reporting System) data from 2021 Q1 - 2024 Q4 (post-COVID) to ensure more accurate and relevance in results. Each quarterly FAERS data release contains seven entities such as demographics, drugs, reactions, outcomes, indications, etc. linked with a primary identification attribute.

<img width="574" alt="Data-Source" src="https://github.com/user-attachments/assets/4e7a23d9-c8c7-4ec4-9b22-529c3744072e">

## <a name= "tech"></a>Technologies Used (So far)
* Data Analysis and Transformation : Pandas
* Regression-based Imputation : Scikit-learn
* Association Rule Mining : fpgrowth_py
* Data Visualization : Matplotlib, Seaborn
* Web Framework : Streamlit
* Version Control : Git
* Auditing/ Quick Data Validation: MS Excel

## <a name= "method"></a>Data Preprocessing

### <a name= "demo-prep"></a>Data Preprocessing (Demographics)
* Extracted only required columns from FAERS data.
* Filtered pediatric population records based on age.
* Converted all age units to years and classified into age bins (teenagers, neonates, etc.).
* Removed outliers (e.g., unrealistic ages, unknown genders).
* Created a unified 'origin country' feature from FAERS records.
* Filtered only to retreive cases which are newly initiated post-COVID.

### <a name= "impute"></a>Weight Imputation
* Issue: Over 70% of weight values missing. Age distribution is imbalanced.
* Solution: Machine Learning-based Imputation and a model for each age distribution.
* Trained three models: Random Forest, Gradient Boosting, XGBoost.
* Evaluation Metrics: R² Score, RMSE, MAE, MAPE.
* Final Model: Random Forest as it preserves data distribution.

### <a name= "drug-prep"></a>Data Preprocessing (Drugs)
* Only the drug cases connected to the above filtered demographics cases were selected first.
* Handling duplicate values for attribute 'PROD_AI' using look-up tables

## <a name= "modular"></a>Modularized Data Preprocessing
For each entity: Demographics, Drugs, Reactions and Outcomes, the preprocessing will be done through the use of modular scripts to maintain simplicity and ease of debugging and encapsulate business logic. The usage of the modularized scripts is documented below. Furthermore, the use of process logs at each transformation helped to find errors during the debug process.

### <a name= "using"></a>Usage

### Clone the repository
```
git clone https://github.com/kisaraF/Pediatric-ADR-DDI-Tool.git
cd Pediatric-ADR-DDI-Tool
```

### Running Scripts
First add the raw data into each folder in `Data/RAW_DATA/`


#### Apply Transformations (Demographics)
```
python Transform_Script_demog.py
```

#### Combine transformed demographics data and remove duplicates
```
python combine_transformed_files_demog.py
```

#### Use the regression-based imputation model to predict missing values
```
python predict_missing_values_demog.py
```

#### Apply Transformations (Drugs)
```
python apply_drug_trans.py
```

#### Apply Transformations (Outcomes & Reactions)
```
python apply_other_transforms.py
```

## <a name= "assocr"></a>Association Rule Mining
* Before mining rules the each entity had to be concatenated into one single case (row) using the 'primaryid' and create a transaction set. 
* A prefix to identify each entity must be used (drug_, demo_, reac_, outc_), which is crucial for mining rules.
* Once all the entities are combined and the transaction set is created, rule mining takes place. For this application `minsup : 0.003` and `minconf : 0.9` was used. 

## <a name= "outc_sev"></a>Outcome Severity Mining
* Once the rules are mined, cinically qualified rules were filtered out which has at least one drug, one reaction reported along with demographics- `age_bin`, `origin_country` and `sex`
* From the original transaction set used for rule mining, similar cases which includes the above filtered rules will be selected.
* Next, from those rules, their outcome will be extracted for each case and the severity will be assessed based on the distribution and proportion.

## <a name= "dashboard"></a>Streamlit App
* Streamlit App Link – <a href='https://pediatric-adr-ddi-tool-kisaraf.streamlit.app/'>link</a>
* The rules mined and the outcome severity assessed in above steps will be stored in the form of JSON and CSV respectively and will be imported using 'cache_data' method of Streamlit for re-use without reloading. 
* The user can input:
	* Age category
	* Origin country
	* Weight class
	* Gender
	* Prescribed drugs
* If a matching case is identified, potential reactions and reported similar cases' outcome severity will be presented.

<img width="650" alt="App-SS" src="https://github.com/user-attachments/assets/a82671a0-1250-4e7a-8505-413a6104b0f7">

## <a name= "access"></a>Accessing Raw Data
* FDA quarterly publications – <a href='https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html'>link</a>
* Quick access (saves hassle of unzipping and selecting each file) - <a href='https://drive.google.com/drive/folders/1g561wpNAcK3QvFaqeqVWhvjjKbEaoZU3?usp=drive_link'>link</a>
