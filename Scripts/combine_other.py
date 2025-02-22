import pandas as pd
import os
import glob

reactions_fp = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\REACTIONS'
outcomes_fp = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\OUTCOMES'

print('''
To combine Outcomes press 1
To combine Reactions press 2
      ''')
prompt = input('Your prompt: ')

if prompt == '2':
    def combineReactions():
        num_reactions_files = os.listdir(reactions_fp)
        
        for i in num_reactions_files:
            print(i)
        
        print('\n\n')

        def combineFiles(f_path):
            # Find all CSV files in the specified folder
            files = glob.glob(os.path.join(f_path, "*.csv")) 
            
            #Read each file and combine them together
            df_ls = [pd.read_csv(i) for i in files]
            combined_df = pd.concat(df_ls, ignore_index= True)

            print(f'Total Number of Lines: {len(combined_df)}\n')
        
            return combined_df

        #Execute Functions
        combined_reacs= combineFiles(reactions_fp)

        #Export the file
        combined_reacs.to_csv('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\CLEAN_DATA/reactions.csv', index=False)

        #No need to remove duplicates as the reactions are one to many related with the primaryid

    combineReactions()

elif prompt == '1':
    def combineOutcomes():
        num_reactions_files = os.listdir(outcomes_fp)
        
        for i in num_reactions_files:
            print(i)
        
        print('\n\n')

        def combineFiles(f_path):
            # Find all CSV files in the specified folder
            files = glob.glob(os.path.join(f_path, "*.csv")) 
            
            #Read each file and combine them together
            df_ls = [pd.read_csv(i) for i in files]
            combined_df = pd.concat(df_ls, ignore_index= True)

            print(f'Total Number of Lines: {len(combined_df)}\n')
        
            return combined_df

        #Execute Functions
        combined_reacs= combineFiles(outcomes_fp)

        #Export the file
        combined_reacs.to_csv('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\CLEAN_DATA/outcomes.csv', index=False)

        #No need to remove duplicates as the reactions are one to many related with the primaryid

    combineOutcomes()

else:
    print('Try again!')
