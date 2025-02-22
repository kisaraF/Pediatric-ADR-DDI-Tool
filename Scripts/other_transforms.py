import pandas as pd

#Import the csv file
def importFile(file_path):
    drug_df = pd.read_csv(file_path, sep='$')
    return drug_df


#Import Demographic and get primaryids
def demo_pid_extraction(file_path):
    demo_df = pd.read_csv(file_path)
    pids = list(demo_df['primaryid'])
    return pids


#Select drug records that are only in the demographic primary ids
def pid_Filteration(df, demo):
    df_1 = df[df['primaryid'].isin(demo)]
    return df_1


#Only select the necessary attributes
def final_df_reactions(df):
    d_set = df[['primaryid', 'caseid', 'pt']]
    return d_set

def final_df_outcomes(df):
    return df

#Export as CSV
def exportCSV(df, out_path):
   df.to_csv(out_path, index=False)
   return f"Successfully exported to {out_path}"
