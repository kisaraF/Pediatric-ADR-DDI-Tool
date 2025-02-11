from faers_transforms import demo_transform_funcs
import pendulum
import pandas as pd

now = pendulum.now('Asia/Colombo')
#now.format('YYYY-MM-DD HH:mm:ss')

def TransformDemos(file_path, out_path):
    #Import as CSV
    raw_df = demo_transform_funcs.importFile(file_path)
    import_log = f'{file_path} imported at: {now.format('YYYY-MM-DD HH:mm:ss')}'

    #Step 01: Select only the necessary columns
    raw_df_filt = demo_transform_funcs.rawDfFiltered(raw_df)
    attribute_filter_log = f'\nAttributes filtered from raw file at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Step 02: Selecting only the pediatric population
    demo_pedi_raw = demo_transform_funcs.pediRaw(raw_df_filt)
    pedi_filter_log = f'\nPediatric population filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

    #Step 03: Checking if there are age values without age_code values from the age_grp selection
    demo_pedi_raw = demo_transform_funcs.checkAges01(demo_pedi_raw)
    age_filter_1_log = f'\nAge Check 01 filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

    #Step 04: Check if there are age values that misses the age_cod that are from filtered < 19 data without a age_grp value
    demo_pedi_raw = demo_transform_funcs.checkAges02(demo_pedi_raw)
    age_filter_2_log = f'\nAge Check 02 filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

    #Step 05: It's important to disregard age values (which are in years) that are higher than 18
    demo_pedi_raw = demo_transform_funcs.checkAges03(demo_pedi_raw)
    age_filter_3_log = f'\nAge Check 03 filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

    #Step 06: Remove age_cod as DEC
    demo_pedi_raw = demo_transform_funcs.removeDEC(demo_pedi_raw)
    dec_rm_log = f'\nDEC age codes removed at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

    #Step 07: Convert all ages into standard year format
    demo_pedi_raw_1 = demo_transform_funcs.ageYrStandard(demo_pedi_raw)
    age_conv_log = f'\nAges converted to year standard at: {now.format('YYYY-MM-DD HH:mm:ss')} | Columns: {demo_pedi_raw_1.columns}\n'

    #Step 08: Binning the age values
    demo_pedi_raw_2 = demo_transform_funcs.ageBinning(demo_pedi_raw)
    age_bins_log = f'\nAges binned at: {now.format('YYYY-MM-DD HH:mm:ss')} | Columns: {demo_pedi_raw_2.columns}\n'

    #Step 09: Remove all the NA_VAL that has missing values in age and age_cod
    demo_pedi_raw_2_copy = demo_pedi_raw_2.copy()
    demo_pedi_raw_2_copy = demo_transform_funcs.rmNA_VALbins(demo_pedi_raw_2_copy)
    na_val_rm_log = f'\nFirst wave of NA_VAL removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_2_copy)} records preserved\n'

    #Step 10: If still there are NA_VAL values, disregard them
    demo_pedi_raw_2_copy = demo_transform_funcs.rmNA_VALbins_2(demo_pedi_raw_2_copy)
    na_val_rm_log_2 = f'\nSecond wave of NA_VAL removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_2_copy)} records preserved\n'

    #Step 11: Remove all gender values that are missing
    demo_pedi_raw_4 = demo_transform_funcs.dropMissingSex(demo_pedi_raw_2_copy)
    rm_missing_sex_log = f'\nMissing gender values removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_4)} records preserved\n'

    #Step 12: Only keep genders that are either M or F
    demo_pedi_raw_3 = demo_transform_funcs.genderFilter(demo_pedi_raw_4)
    sex_filter_log = f'\nSelected only M or F genders at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    #Step 13: Fix the missing values in the reporter country
    demo_pedi_raw_5 = demo_transform_funcs.getOriginCountry(demo_pedi_raw_3)
    fix_country_log = f'\nOrigin country added at: {now.format('YYYY-MM-DD HH:mm:ss')} |  Columns: {demo_pedi_raw_5.columns}\n'

    #Step 14: remove all 'Country not specified' values from origin country
    demo_pedi_raw_6 = demo_transform_funcs.rmMissingOrigin(demo_pedi_raw_5)
    rm_missing_origin_log = f'\nMissing origin values removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_6)} records preserved\n'

    #Step 15: Convert lbs values to kg
    demo_pedi_raw_7 = demo_transform_funcs.convLbsToKg(demo_pedi_raw_6)
    wt_conv_log = f'\nWeights converted to KG at: {now.format('YYYY-MM-DD HH:mm:ss')} |  Columns: {demo_pedi_raw_7.columns}\n'

    #Step 16: Let's remove all weight values that has a wt value but not a wt_cod
    demo_pedi_raw_8 = demo_transform_funcs.wtCheck01(demo_pedi_raw_7)
    wtcheck01_log = f'\nWeight Check 01 happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_8)} records preserved\n'

    #Step 17: Let's check the validity in weights
    demo_pedi_raw_9 = demo_transform_funcs.findWtOutliers(demo_pedi_raw_8)
    wtcheck02_log = f'\nWeight Check 02 (Outliers) happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  Columns: {demo_pedi_raw_9.columns}\n'

    #Step 18: Now disregard invalid weights
    demo_pedi_raw_10 = demo_transform_funcs.rmWtOutliers(demo_pedi_raw_9)
    wtcheck03_log = f'\nWeight Check 03 (outlier removal) happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_10)} records preserved\n'

    #Step 19: Remove all ages where the age is just 0
    demo_pedi_raw_11 = demo_transform_funcs.removeZeroAge(demo_pedi_raw_10)
    remove_zero_ages_log = f'\nRemoving ages just 0 happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_11)} records preserved\n'
    
    #Step 20: Only get the necessary columns (Final Transformed layer)
    demo_pedi_transformed = demo_transform_funcs.finalLayer(demo_pedi_raw_11)
    final_layer_log = f'\nFinal Transformed Layer selected at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_transformed)} records preserved\n'

    #Step 21: Export to csv
    export_to_csv = demo_transform_funcs.exportCSV(demo_pedi_transformed, out_path)
    export_msg =  f'\n{export_to_csv} at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

    log_entries = [import_log,attribute_filter_log, pedi_filter_log, age_filter_1_log, age_filter_2_log, 
               age_filter_3_log, dec_rm_log, age_conv_log, age_bins_log, na_val_rm_log, na_val_rm_log_2, 
               rm_missing_sex_log, sex_filter_log, fix_country_log, rm_missing_origin_log, wt_conv_log, 
               wtcheck01_log, wtcheck02_log, wtcheck03_log, remove_zero_ages_log, final_layer_log, export_msg]
    
    log_name = f'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Process_Logs\\DEMOGRAPHICS/Transform_Log_{file_path[-12:][:8]}.txt'

    with open(log_name, 'w') as f:
        for i in log_entries:
            f.write(i)

