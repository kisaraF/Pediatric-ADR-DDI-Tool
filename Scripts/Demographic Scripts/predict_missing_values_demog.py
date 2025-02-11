from faers_transforms import predict_missing_values_funcs as prm
import pandas as pd
import pendulum

now = pendulum.now('Asia/Colombo')

#Import the transformed master which contains unique records
file_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\Transformed/DEMO_MASTER.csv'
init_df = pd.read_csv(file_path)

def doIt():
#----------------------------------  Feature Encoding  ----------------------------------

    #Clean up the data frame
    df_1 = prm.cleanDF(init_df)
    log_entry_1 = f'\nSelected only needed features ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_1)

    #Normalize the age values
    df_2 = prm.normAge(df_1)
    log_entry_2 = f'\nNormalized age values ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_2)

    #Encode gender values
    df_3 = prm.featureEncodeSex(df_2)
    log_entry_3 = f'\nEncoded gender values ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_3)

    #Encoding age bins
    df_4 = prm.encodeAgeBin(df_3)
    log_entry_4 = f'\nEncoded age bin values ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_4)

    #Get the unique country lookup data frame
    unique_country_df = prm.uniqueCountryLookup(df_4)
    log_entry_5 = f'\nNumber of unique countries : {len(unique_country_df)} ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_5)

    #Encode country values
    df_5 = prm.encodeCountry(df_4, unique_country_df)
    log_entry_6 = f'\nEncoded country values ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_6)

    #Cleaning up for model training
    feature_df = prm.readyDF(df_5)
    log_entry_7 = f'\nCleaned up data frame for predictions ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_7)

#-----------------------------------------  Getting Predictions  ----------------------------------------

    #Selecting features
    train_ready_df = prm.featureSelection(feature_df)

    #Getting predictions
    preds_array = prm.predictArray(train_ready_df)
    log_entry_8 = f'\nMade predictions ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_8)

    #Merging the predicted values to the original 
    feature_df['wt_kg'] = preds_array

#-----------------------------------  Merging the 2 datasets together  -----------------------------    
    
    #Only select the columns that's needed for the merge
    df_complete = prm.completeDF(init_df)

    predicted_df = feature_df[['primaryid', 'caseid', 'i_f_code', 'age_yrs', 'age_bin', 
                               'sex', 'Origin_country', 'wt_kg', 'init_fda_dt', 'fda_dt']]
    
    demog_clean_df = pd.concat([predicted_df, df_complete], ignore_index=False)
    demog_clean_df.to_csv('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\Clean-Data/demographics.csv', index = False)

doIt()

