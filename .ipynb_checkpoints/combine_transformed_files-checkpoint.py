import pandas as pd
import os
import glob

file_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\Transformed'
files_in_path = os.listdir(file_path)

print(f'\n----Files in the specified folder----\n')

for i in files_in_path:
    print(i)

print('\n')

def combineFiles(f_path):
    # Find all CSV files in the specified folder
    files = glob.glob(os.path.join(f_path, "*.csv")) 
    
    #Read each file and combine them together
    df_ls = [pd.read_csv(i) for i in files]
    combined_df = pd.concat(df_ls, ignore_index= True)

    print(f'Total Number of Lines before removing duplicates: {len(combined_df)}')

    #Export the duplicated one just to double check
    combined_df.to_csv('combined_df.csv', index=False)

    return combined_df

def removeDuplicates(df):
    clean_df = df.drop_duplicates(subset=['caseid'])
    clean_df.to_csv('Data/Transformed/DEMO_MASTER.csv', index=False)
    
    print(f'Total number of rows after removing duplicates: {len(clean_df)}')

#Execute Functions
combined_file = combineFiles(file_path)

removeDuplicates(combined_file)

