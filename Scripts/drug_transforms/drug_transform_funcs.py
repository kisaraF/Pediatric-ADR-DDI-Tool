import pandas as pd
import numpy as np

#Import the csv file
def importFile(file_path):
    drug_df = pd.read_csv(file_path, sep='$')
    return drug_df

#Import Demographic and get primaryids
def demo_pid_extraction(file_path):
    demo_df = pd.read_csv(file_path)
    pids = list(demo_df['primaryid'])
    return pids

#Select only the necessary columns
def rawDfFiltered(df):
    drug_df_2 = df[['primaryid', 'caseid', 'drug_seq', 'role_cod', 'drugname', 'prod_ai']]
    return drug_df_2

#Removing drugnames with null values
def removeNullDrugs(df):
    df_raw_2 = df[df['drugname'].isna() == False]
    return df_raw_2

#Select drug records that are only in the demographic primary ids
def drug_Filteration(drg, demo):
    df_1 = drg[drg['primaryid'].isin(demo)]
    return df_1

#----Making the lookup table (All Processes)
def lookup_1(df):
    lookup_1 = df[['drugname', 'prod_ai']]
    lookup_1.drop_duplicates(inplace= True) #Remove duplicates
    return lookup_1

#Getting the count of each drugname that gets repeated
def lookupCounts(df):
    lookup_counts = df.groupby('drugname').size().reset_index(name='Count').sort_values(by=['Count'], ascending=False)
    lookup_counts = lookup_counts[lookup_counts['Count'] > 1]
    return lookup_counts

def removeNAs(df, temp_1):
    # Create a boolean mask using & (bitwise AND) instead of 'and'
    mask = (df['drugname'].isin(temp_1)) & (df['prod_ai'].isna())
    
    # Apply the mask to create a new column with 'Remove' or 'Keep'
    df['Action'] = df.apply(lambda row: 'Remove' if mask[row.name] else 'Keep', axis=1)

    return df


#Removing layer_1 duplicate NaNs
def removeNAs_L1(df):
    lookup_2 = df[df['Action'] == 'Keep']
    return lookup_2

#Getting the count of each drugname that gets repeated V2
def lookupCounts_2(df):
    temp_2 = df.groupby('drugname').size().reset_index(name='Count').sort_values(by=['Count'], ascending= False)
    temp_2 = temp_2[temp_2['Count'] > 1]
    return temp_2


#Removing layer_2 duplicate NaNs
def removeNAs_L2(df):
    df['wc_len'] = df['prod_ai'].str.len()
    df['wc_rnk'] = df.groupby('drugname')['wc_len'].rank(method='dense', ascending=False)
    lookup_3 = df[df['wc_rnk'] != 2]
    return lookup_3

#Filling missing values in the lookup table
def fillMissingLookup(df):
    if pd.isna(df['prod_ai']):
        return 'NA'
    else:
        return df['prod_ai']
    

#Applying filling
def applyMissingValsFiller(df):
    df['corr_prod_ai'] = df.apply(fillMissingLookup, axis=1)
    lookup_4 = df[['drugname', 'corr_prod_ai']] #Selecting the final version of lookup table
    return lookup_4

#Filling missing prod_ai values and final selection
def finalTrans(df, lookup):
    df_raw_3 = pd.merge(left = df, right = lookup, how = 'left', left_on = 'drugname', right_on='drugname')
    df_raw_4 = df_raw_3[['primaryid', 'caseid', 'drug_seq', 'role_cod', 'drugname', 'corr_prod_ai']]
    return df_raw_4

#Export as CSV
def exportCSV(df, out_path):
   df.to_csv(out_path, index=False)
   return f"Successfully exported to {out_path}"

