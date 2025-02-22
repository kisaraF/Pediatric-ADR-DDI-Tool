import pendulum
import pandas as pd
import other_transforms

now = pendulum.now('Asia/Colombo')

#Import and extract demogaphic pids
demo_file = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\CLEAN_DATA/demographics.csv'
demo_pids = other_transforms.demo_pid_extraction(demo_file)

def TransformReactions(file_path, out_path):
    #Import as CSV
    raw_df = other_transforms.importFile(file_path)
    import_log = f'{file_path} imported at: {now.format('YYYY-MM-DD HH:mm:ss')}'

    #Extracting only needed reactions records
    reac_df_intrm_1 = other_transforms.pid_Filteration(raw_df, demo_pids) 
    trans_log_1 = f'\nSelected only necessary records (Reactions): {now.format('YYYY-MM-DD HH:mm:ss')} | {len(reac_df_intrm_1)} records preserved\n'

    #Final Dataset
    reac_df_final = other_transforms.final_df_reactions(reac_df_intrm_1)
    trans_log_2 = f'\nSelected only necessary attributes (Reactions): {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Export
    other_transforms.exportCSV(reac_df_final, out_path)
    final_trans_log = f'\nTransformed Reactions File exported at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    log_entries = [import_log, trans_log_1, trans_log_2, final_trans_log]

    log_name = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Process_Logs\\REACTIONS/Transform_Log_{file_path[-12:][:8]}.txt'

    with open(log_name, 'w') as f:
        for i in log_entries:
            f.write(i)


def TransformOutcomes(file_path, out_path):
    #Import as CSV
    raw_df = other_transforms.importFile(file_path)
    import_log = f'{file_path} imported at: {now.format('YYYY-MM-DD HH:mm:ss')}'

    #Extracting only needed outcomes records
    outc_df_intrm_1 = other_transforms.pid_Filteration(raw_df, demo_pids) 
    trans_log_1 = f'\nSelected only necessary records (Outcomes): {now.format('YYYY-MM-DD HH:mm:ss')} | {len(outc_df_intrm_1)} records preserved\n'

    #Final Dataset
    outc_df_final = other_transforms.final_df_outcomes(outc_df_intrm_1)
    trans_log_2 = f'\nSelected only necessary attributes (Outcomes): {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Export
    other_transforms.exportCSV(outc_df_final, out_path)
    final_trans_log = f'\nTransformed Outcomes File exported at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    log_entries = [import_log, trans_log_1, trans_log_2, final_trans_log]

    log_name = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Process_Logs\\OUTCOMES/Transform_Log_{file_path[-12:][:8]}.txt'

    with open(log_name, 'w') as f:
        for i in log_entries:
            f.write(i)   