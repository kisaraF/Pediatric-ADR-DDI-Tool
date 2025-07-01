import pandas as pd
import glob
import os
import transform_other_data 

reactions_fp = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\RAW_DATA\\REACTIONS'
outcomes_fp = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\RAW_DATA\\OUTCOMES'

reaction_files = os.listdir(reactions_fp)
outcomes_files = os.listdir(outcomes_fp)

print('''
To transform Outcomes press 1
To transform Reactions press 2
      ''')
prompt = input('Your prompt: ')


if prompt == '2':
    #Transforming reactions
    for i in reaction_files:
        file_path = f'{reactions_fp}/{i}'
        out_path = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\REACTIONS/{i[:8]}_TRANSFORMED.csv'
        transform_other_data.TransformReactions(file_path, out_path)
        print(f'{file_path[-12:][:8]} transformed\n\n')
elif prompt == '1':
    #Transforming outcomes
    for i in outcomes_files:
        file_path = f'{outcomes_fp}/{i}'
        out_path = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\OUTCOMES/{i[:8]}_TRANSFORMED.csv'
        transform_other_data.TransformOutcomes(file_path, out_path)
        print(f'{file_path[-12:][:8]} transformed\n\n')
else:
    print('Try again!')