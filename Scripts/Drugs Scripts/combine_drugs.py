import pandas as pd
import os
import glob

file_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\DRUGS'
files_in_path = os.listdir(file_path)

for i in files_in_path:
    print(i)

print('\n')

def combineFiles(f_path):
    # Find all CSV files in the specified folder
    files = glob.glob(os.path.join(f_path, "*.csv")) 
    
    #Read each file and combine them together
    df_ls = [pd.read_csv(i) for i in files]
    combined_df = pd.concat(df_ls, ignore_index= True)

    print(f'Total Number of Lines: {len(combined_df)}\n')
    
    return combined_df

#Execute Functions
combined_drugs= combineFiles(file_path)

#Export the file
combined_drugs.to_csv('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\CLEAN_DATA/drugs_data.csv')


# no need to remove duplicates as the primary ids selected at each transformations are unique ones
# and all the unique number of pids in clean data and combined drug data is the same
