import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
# import matplotlib.pyplot as plt
# import seaborn as sns
# %matplotlib inline


#Import the csv file
def importFile(file_path):
    demo_df = pd.read_csv(file_path, sep='$')
    return demo_df

#Step 01: Filter only the necessary columns (attributes)
def rawDfFiltered(df):
    demo_df_2 = df[['primaryid', 'caseid', 'i_f_code', 'age', 'age_cod', 'age_grp', 'sex', 'wt', 'wt_cod', 
                    'init_fda_dt', 'fda_dt', 'reporter_country', 'occr_country']]
    return demo_df_2


#Step 02: Selecting only the pediatric population
age_grps = ['N', 'I', 'C', 'T']

def pediRaw(df):
    demo_pedi_raw = df[(df['age_grp'].isin(age_grps)) | ((df['age_grp'].isna()) & (df['age']<19))]
    return demo_pedi_raw

#Step 03: Checking if there are age values without age_code values from the age_grp selection
def checkAges01(df):
    recs = len(df[(df['age'].isna() == False) & (df['age_cod'].isna() == True) & (df['age_grp'].isna() == True)])
    if recs > 0:
        demo_pedi_raw = df[~((df['age'].isna() == False) & (df['age_cod'].isna() == True) & (df['age_grp'].isna() == True))]
        return demo_pedi_raw
    else:
        return df
    
#Step 04: Check if there are age values that misses the age_cod that are from filtered < 19 data without a age_grp value
def checkAges02(df):
    recs = len(df[(df['age'].isna() == False) & (df['age_cod'].isna() == True) & (df['age_grp'].isna() == False)])
    if recs > 0:
        demo_pedi_raw = df[~((df['age'].isna() == False) & (df['age_cod'].isna() == True) & (df['age_grp'].isna() == False))]
        return demo_pedi_raw
    else:
        return df

#Step 05: It's important to disregard age values (which are in years) that are higher than 18
def checkAges03(df):
    recs = len(df[(df['age'] > 18) & (df['age_cod'] == 'YR')])
    if recs > 0:
        demo_pedi_raw = df[~((df['age'] > 18) & (df['age_cod'] == 'YR'))]
        return demo_pedi_raw
    else:
        return df
    
#Step 06: Remove age_cod as DEC
def removeDEC(df):
    demo_pedi_raw = df[df['age_cod'] != 'DEC']
    return demo_pedi_raw

# Function to convert ages into year standard
def convertMt_Yr(df):
  if df['age_cod'] == 'MON':
    conv= round(df['age'] / 12,2)
    return conv
  elif df['age_cod'] == 'WK':
    conv = round(df['age'] / 52.1429, 2)
    return conv
  elif df['age_cod'] == 'DY':
    conv = round(df['age']/ 365, 2)
    return conv
  elif df['age_cod'] == 'HR':
    conv = round(df['age']/8760, 2)
    return conv
  elif df['age_cod'] == 'YR':
    return df['age']
  
#Step 07: Convert age values into years
def ageYrStandard(dataframe):
    dataframe['age_yrs'] = dataframe.apply(convertMt_Yr, axis=1)
    return dataframe

#A function for binning ages
def age_Bins(df):
  if df['age_yrs'] < 0.08:
    return "Neonate"
  elif df['age_yrs'] >= 0.08 and df['age_yrs'] < 1:
    return "Infant"
  elif df['age_yrs'] >= 1 and df['age_yrs'] < 4:
    return "Toddler"
  elif df['age_yrs'] >= 4 and df['age_yrs'] < 7:
    return "Preschooler"
  elif df['age_yrs'] >=7 and df['age_yrs'] < 13:
    return "Child"
  elif df['age_yrs'] >=13 and df['age_yrs'] < 19:
    return "Teenager"
  else:
    return "NA_VAL"

#Step 08: Binning the age values
def ageBinning(dataframe):
   dataframe['age_bin'] = dataframe.apply(age_Bins,axis=1)
   return dataframe

#Step 09: Remove all the NA_VAL that has missing values in age and age_cod
def rmNA_VALbins(df):
   df = df[df['age'].isna()==False]
   return df

#Step 10: If still there are WTF values, disregard them
def rmNA_VALbins_2(df):
   df = df[df['age_bin'] != 'NA_VAL']
   return df

#Step 11: Apply the min-max scaler
scaler = MinMaxScaler(feature_range=(0, 1)) #Instantiate the scaler first

def normalizeAges(df):
   df['age_norm'] = scaler.fit_transform(df[['age']])
   return df

#Step 12: Remove all gender values that are missing
def dropMissingSex(df):
   df = df.dropna(subset=['sex'])
   return df

#A function to Fixing origin country issue
def fix_country(df):
    if (df['reporter_country'] == 'COUNTRY NOT SPECIFIED') & (not pd.isna(df['occr_country'])):
        return df['occr_country']
    elif (df['reporter_country'] != 'COUNTRY NOT SPECIFIED') & (not pd.isna(df['occr_country'])):
        return df['occr_country']
    elif (df['reporter_country'] == 'COUNTRY NOT SPECIFIED') & (pd.isna(df['occr_country'])):
        return 'COUNTRY NOT SPECIFIED'
    elif (df['reporter_country'] != 'COUNTRY NOT SPECIFIED') & (pd.isna(df['occr_country'])):
        return df['reporter_country']

#Step 13: Fix the missing values in the reporter country
def getOriginCountry(dataframe):
   dataframe['Origin_country'] = dataframe.apply(fix_country, axis=1)
   return dataframe


#Step 14: remove all 'Country not specified' values from origin country
def rmMissingOrigin(df):
   df = df[df['Origin_country'] != 'COUNTRY NOT SPECIFIED']
   return df


#A function to convert lbs values to kg
def lbs_to_kg(df):
  if not pd.isna(df['wt_cod']):
    if df['wt_cod'] == 'LBS':
      conv = df['wt'] / 2.2
      return conv
    elif df['wt_cod'] == 'KG':
      return df['wt']
    
#Step 15: Convert lbs values to kg
def convLbsToKg(dataframe):
   dataframe['wt_kg'] = dataframe.apply(lbs_to_kg, axis=1)
   return dataframe

#Step 16: Let's remove all weight values that has a wt value but not a wt_cod
def wtCheck01(df):
   df = df[~((df['wt_cod'].isna() == True) & (df['wt'].isna() == False))]
   return df

#removing outlier values
#A function to check validity of weights
def check_wt_validity(df):
  if pd.isna(df['wt_kg']):
    return "Missing weight"
  else:
    if df['age_bin'] == 'Neonate':
      if (df['wt_kg'] >= 2.5) and (df['wt_kg'] < 4.5):
        return "Valid Weight"
      else:
        return "Invalid Weight"
    elif df['age_bin'] == 'Infant':
      if (df['wt_kg'] >= 4.4) and (df['wt_kg'] < 11.3):
        return "Valid Weight"
      else:
        return "Invalid Weight"
    elif df['age_bin'] == 'Toddler':
      if (df['wt_kg'] >= 8.5) and (df['wt_kg'] < 17.5):
        return "Valid Weight"
      else:
        return "Invalid Weight"
    elif df['age_bin'] == 'Preschooler':
      if (df['wt_kg'] >= 12.5) and (df['wt_kg'] < 25.8):
        return "Valid Weight"
      else:
        return "Invalid Weight"
    elif df['age_bin'] == 'Child':
      if (df['wt_kg'] >= 19.8) and (df['wt_kg'] < 51):
        return "Valid Weight"
      else:
        return "Invalid Weight"
    elif df['age_bin'] == 'Teenager':
      if (df['wt_kg'] >= 39) and (df['wt_kg'] < 81):
        return "Valid Weight"
      else:
        return "Invalid Weight"


#Step 17: Let's check the validity in weights
def findWtOutliers(dataframe):
   dataframe['Valid_Wt'] = dataframe.apply(check_wt_validity, axis=1)
   return dataframe

#Step 18: Now disregard invalid weights
def rmWtOutliers(df):
   df = df[df['Valid_Wt'] != 'Invalid Weight']
   return df

#Step 19: Only get the necessary columns
def finalLayer(df):
   df = df[['primaryid', 'caseid', 'i_f_code', 'age_yrs', 'age_bin', 'age_norm', 'sex', 'wt_kg', 'Origin_country', 'init_fda_dt', 'fda_dt']]
   return df

#Step 20: Export as CSV
def exportCSV(df, out_path):
   df.to_csv(out_path, index=False)
   return f"Successfully exported to {out_path}"

