from faers_transforms import predict_missing_values_funcs as prm
import pandas as pd
import pendulum

now = pendulum.now('Asia/Colombo')

#Import the transformed master which contains unique records
file_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\DEMOGRAPHICS/DEMO_MASTER.csv'
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

    #Cleaning up for model predictions
    feature_df = prm.readyDF(df_5)
    #feature_df.to_csv('temp.csv', index=False)
    log_entry_7 = f'\nCleaned up data frame for predictions ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_7)

#-----------------------------------------  Splitting Dataset to age groups  ----------------------------------------

    #age group 1 
    age_grp_1 = prm.df_age_grp_1(feature_df)
    age_grp_1.to_csv('age_grp_1.csv', index=False)
    log_entry_8 = f'\nAge group 1 splitted ({now.format('YYYY-MM-DD HH:mm:ss')})\n'

    #age group 2 
    age_grp_2 = prm.df_age_grp_2(feature_df)
    age_grp_2.to_csv('age_grp_2.csv', index=False)
    log_entry_9 = f'\nAge group 2 splitted ({now.format('YYYY-MM-DD HH:mm:ss')})\n'

    #age group 3 
    age_grp_3 = prm.df_age_grp_3(feature_df)
    age_grp_3.to_csv('age_grage_grp_3.csv', index=False)
    log_entry_10 = f'\nAge group 3 splitted ({now.format('YYYY-MM-DD HH:mm:ss')})\n'


#-----------------------------------------  Getting Predictions  ----------------------------------------

    #Selecting features
    train_ready_df_1 = prm.featureSelection(age_grp_1)
    train_ready_df_2 = prm.featureSelection(age_grp_2)
    train_ready_df_3 = prm.featureSelection(age_grp_3)

    #Getting predictions
    preds_array_1 = prm.predictArray_1(train_ready_df_1)
    preds_array_2 = prm.predictArray_2(train_ready_df_2)
    preds_array_3 = prm.predictArray_3(train_ready_df_3)
    log_entry_11 = f'\nMade predictions ({now.format('YYYY-MM-DD HH:mm:ss')})\n'
    print(log_entry_11)

    #Merging the predicted values to the original 
    # train_ready_df_1['wt_kg'] = preds_array_1
    # train_ready_df_2['wt_kg'] = preds_array_2
    # train_ready_df_3['wt_kg'] = preds_array_3

    age_grp_1['wt_kg'] = preds_array_1
    age_grp_2['wt_kg'] = preds_array_2
    age_grp_3['wt_kg'] = preds_array_3

    #age_grp_1.to_csv('hey.csv', index=False)
    

#-----------------------------------  Merging the 2 datasets together  -----------------------------    

    #merging all 3 predicted datasets together
    predicted_master_df = pd.concat([age_grp_1, age_grp_2, age_grp_3])
    predicted_master_df.to_csv('predict_master.csv', index=False)
    
    #Only select the columns that's needed for the merge
    df_complete = prm.completeDF(init_df)

    predicted_df = predicted_master_df[['primaryid', 'caseid', 'i_f_code', 'age_yrs', 'age_bin', 
                               'sex', 'Origin_country', 'wt_kg', 'init_fda_dt', 'fda_dt']]
    
    demog_clean_df = pd.concat([predicted_df, df_complete], ignore_index=False)
    demog_clean_df.to_csv('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\CLEAN_DATA/demographics.csv', index = False)

doIt()

