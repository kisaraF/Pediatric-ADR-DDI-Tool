#For predicting missing weight values and completing the dataset
import pandas as pd
from demog_wt_model import pred_model
from sklearn.preprocessing import MinMaxScaler

#Get the complete data and store in a variable
def completeDF(df):
    df_complete= df[df['wt_kg'].isna() == False]
    df_complete.drop('rnk', axis=1, inplace=True)
    return df_complete

#Get the DF to have only the columns I need & rows without weight values
def cleanDF(df):
    # Remove unnecessary columns
    df = df[['primaryid', 'caseid', 'i_f_code', 'age_yrs', 'age_bin', 'sex', 'wt_kg', 'Origin_country',
             'init_fda_dt', 'fda_dt']]
    
    df_2 = df[df['wt_kg'].isna() == True]
    print(f'Number of rows without wt_kg : {len(df_2)}')
    
    return df_2

#------------------------  FEATURE ENCODING  ----------------------
#Let's normalize the age_yrs
def normAge(df):
    scaler = MinMaxScaler(feature_range=(0, 1))
    df['age_norm'] = scaler.fit_transform(df[['age_yrs']])
    return df

#A function to encode the gender
def encodeGender(df):
    if df['sex'] == 'M':
        return 0
    elif df['sex'] == 'F':
        return 1

#Encoding feature: sex
def featureEncodeSex(df):
    df['gender_enc'] = df.apply(encodeGender, axis=1)
    return df

#A function to encode the age_bin
def age_bin_encode(df):
    if df['age_bin'] == 'Neonate':
        return 0
    elif df['age_bin'] == 'Infant':
        return 1
    elif df['age_bin'] == 'Toddler':
        return 2
    elif df['age_bin'] == 'Preschooler':
        return 3
    elif df['age_bin'] == 'Child':
        return 4
    elif df['age_bin'] == 'Teenager':
        return 5
    else:
        return "YYYY"

#Encoding age_bin
def encodeAgeBin(df):
    df['age_bin_enc'] = df.apply(age_bin_encode, axis=1)
    return df

#Creating a dataframe for origin country for encoding as a look up df
def uniqueCountryLookup(df):
    country_ls = pd.unique(df['Origin_country'])
    val_ls = [i for i in range(0, len(country_ls))]
    uniq_countries = pd.DataFrame({'country':country_ls, 'origin_country_enc':val_ls})
    return uniq_countries

#Encoding country values
def encodeCountry(df, uniq_countries):
    cond_df = pd.merge(left= df, right= uniq_countries, how = 'inner', left_on = 'Origin_country', right_on = 'country')
    return cond_df

#Cleaning the data frame for model training
def readyDF(df):
    clean_df = df[['primaryid', 'caseid', 'i_f_code', 'age_yrs', 'age_bin', 'age_norm', 'age_bin_enc', 'sex', 'gender_enc', 
                   'Origin_country', 'origin_country_enc', 'init_fda_dt', 'fda_dt']]
    return clean_df


#---------------------------------  Model Predictions  ---------------------------------

#Selecting features for model training
def featureSelection(df):
    df = df[['age_norm', 'age_bin_enc', 'gender_enc', 'origin_country_enc']]
    return df

#Predict the missing values
def predictArray(X):
    xgb_model= pred_model.getModel()
    preds = xgb_model.predict(X)
    return preds


