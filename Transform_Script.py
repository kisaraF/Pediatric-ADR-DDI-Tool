from faers_transforms import transform_demos
import os

file_directory = os.listdir('C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\DEMO_FILES')
#print(file_directory)

#Transforming all files at once
for i in file_directory:
    file_path = f'Data/DEMO_FILES/{i}'
    out_path = f'Data/Transformed/{i[:8]}_TRANSFORMED.csv'
    transform_demos.TransformDemos(file_path, out_path)
    print(f'{file_path[-12:][:8]} transformed\n\n')

# file_path = 'Data/DEMO_FILES/DEMO24Q2.txt'
# out_path = 'Data/Transformed/DEMO24Q2.csv'