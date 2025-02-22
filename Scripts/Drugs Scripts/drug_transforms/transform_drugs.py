from drug_transforms import drug_transform_funcs
import pendulum
import pandas as pd

now = pendulum.now('Asia/Colombo')

#Import and extract demogaphic pids
demo_file = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\CLEAN_DATA/demographics.csv'
demo_pids = drug_transform_funcs.demo_pid_extraction(demo_file)

def TransformDrugData(file_path, out_path):
    #Import as CSV
    raw_df = drug_transform_funcs.importFile(file_path)
    import_log = f'{file_path} imported at: {now.format('YYYY-MM-DD HH:mm:ss')}'

    #Select only the necessary columns
    raw_df_filt = drug_transform_funcs.rawDfFiltered(raw_df)
    attribute_filter_log = f'\nAttributes filtered from raw file at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Removing drugnames with nulls
    drug_df_intrm_1 = drug_transform_funcs.removeNullDrugs(raw_df_filt)
    trans_log_1 = f'\nRecords filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(drug_df_intrm_1)} records preserved\n'

    #Extracting only needed drug records
    drug_df_intrm_1 = drug_transform_funcs.drug_Filteration(drug_df_intrm_1, demo_pids) 
    trans_log_9 = f'\nSelected only necessary records: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(drug_df_intrm_1)} records preserved\n'

    #-- Starting on lookup table procedures
    #Lookup layer 1
    lookup_tb_1 = drug_transform_funcs.lookup_1(drug_df_intrm_1)
    trans_log_2 = f'\nLookup_1 created at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Lookup counts temp_1
    temp_1 = drug_transform_funcs.lookupCounts(lookup_tb_1)
    trans_log_3 = f'\nLookup counts temporary table created at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Removal Layer_1
    lookup_tb_2 = drug_transform_funcs.removeNAs(lookup_tb_1, temp_1)
    trans_log_4 = f'\nLookup_2 created at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    lookup_tb_2 = drug_transform_funcs.removeNAs_L1(lookup_tb_2)
    trans_log_5 = f'\nLookup_2 cleansed at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    # #Lookup counts temp_2
    # temp_2 = drug_transform_funcs.lookupCounts_2(lookup_tb_2)
    # trans_log_3 = f'\nLookup counts temporary table 2 created at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Removal Layer_2
    lookup_tb_3 = drug_transform_funcs.removeNAs_L2(lookup_tb_2)
    trans_log_6 = f'\nLookup_3 created at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'
    
    #Handling the missing values in the lookup table 3
    lookup_tb_4 = drug_transform_funcs.applyMissingValsFiller(lookup_tb_3)
    trans_log_6 = f'\nFinal lookup table created at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'


    #Applying the filling for missing prod_ai values
    final_drug_table = drug_transform_funcs.finalTrans(drug_df_intrm_1, lookup_tb_4)
    trans_log_7 = f'\nThis Quarter Drug File was Transformed at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Export as CSV
    drug_transform_funcs.exportCSV(final_drug_table, out_path)
    trans_log_8 = f'\nTransformed File exported at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    log_entries = [import_log,attribute_filter_log, trans_log_1, trans_log_9, trans_log_2, trans_log_3, 
                   trans_log_4, trans_log_5, trans_log_6, trans_log_7, trans_log_8]
    
    log_name = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Process_Logs\\DRUGS/Transform_Log_{file_path[-12:][:8]}.txt'

    with open(log_name, 'w') as f:
        for i in log_entries:
            f.write(i)



