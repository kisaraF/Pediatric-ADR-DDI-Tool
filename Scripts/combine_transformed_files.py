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

    print(f'Total Number of Lines before removing duplicates: {len(combined_df)}\n')

    prompt = input('Would you like to save a copy of the duplicates? (Y/N) ')

    if prompt.upper() == 'Y':
        #Export the duplicated one just to double check
        combined_df.to_csv('combined_df.csv', index=False)
    
    return combined_df

def removeDuplicates(df):
    #When removing duplicates, the latest case should be selected
    sorted_df = df.sort_values(by=['caseid', 'fda_dt'], ascending = [True,False])
    #Grouping each case id, sorting by the latest date and assigning a rank
    sorted_df['rnk'] = sorted_df.groupby('caseid')['fda_dt'].rank(method='first', ascending = False)
    master_df = sorted_df[sorted_df['rnk'] == 1] #Select only the latest records
    
    master_df.to_csv('Data/Transformed/DEMO_MASTER.csv', index=False)
    
    print(f'\nTotal number of rows after removing duplicates: {len(master_df)}')

#Execute Functions
combined_file = combineFiles(file_path)

removeDuplicates(combined_file)

