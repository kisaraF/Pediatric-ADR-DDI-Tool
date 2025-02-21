from drug_transforms import transform_drugs
import pandas as pd
import os

file_directory = os.listdir('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\RAW_DATA\\DRUGS')

#Transforming all files at once
for i in file_directory:
    file_path = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\RAW_DATA\\DRUGS/{i}'
    out_path = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\TRANSFORMED_DATA\\DRUGS/{i[:8]}_TRANSFORMED.csv'
    transform_drugs.TransformDrugData(file_path, out_path)
    print(f'{file_path[-12:][:8]} transformed\n\n')

