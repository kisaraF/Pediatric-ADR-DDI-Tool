#from folder import module_name
import pendulum
import pandas as pd

now = pendulum.now('Asia/Colombo')
#now.format('YYYY-MM-DD HH:mm:ss')

#Maintain a log file of the transformation being applied
#with open('log.txt') as f:


#Import as CSV
raw_df = "module_name".importFile(file_path)
import_log = f'{file_path} imported at: {now.format('YYYY-MM-DD HH:mm:ss')}'

#Step 01: Select only the necessary columns
raw_df_filt = "module_name".rawDfFiltered(raw_df)
attribute_filter_log = f'\nAttributes filtered from raw file at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'

#Step 02: Selecting only the pediatric population
demo_pedi_raw = "module_name".pediRaw(raw_df_filt)
pedi_filter_log = f'\nPediatric population filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

#Step 03: Checking if there are age values without age_code values from the age_grp selection
demo_pedi_raw = "module_name".checkAges01(demo_pedi_raw)
age_filter_1_log = f'\nAge Check 01 filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

#Step 04: Check if there are age values that misses the age_cod that are from filtered < 19 data without a age_grp value
demo_pedi_raw = "module_name".checkAges02(demo_pedi_raw)
age_filter_2_log = f'\nAge Check 02 filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

#Step 05: It's important to disregard age values (which are in years) that are higher than 18
demo_pedi_raw = "module_name".checkAges03(demo_pedi_raw)
age_filter_3_log = f'\nAge Check 03 filtered at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

#Step 06: Remove age_cod as DEC
demo_pedi_raw = "module_name".removeDEC(demo_pedi_raw)
dec_rm_log = f'\nDEC age codes removed at: {now.format('YYYY-MM-DD HH:mm:ss')} | {len(demo_pedi_raw)} records preserved\n'

#Step 07: Convert all ages into standard year format
demo_pedi_raw_1 = "module_name".ageYrStandard(demo_pedi_raw)
age_conv_log = f'\nAges converted to year standard at: {now.format('YYYY-MM-DD HH:mm:ss')} | Columns: {demo_pedi_raw_1.columns}\n'

#Step 08: Binning the age values
demo_pedi_raw_2 = "module_name".ageBinning(demo_pedi_raw)
age_bins_log = f'\nAges binned at: {now.format('YYYY-MM-DD HH:mm:ss')} | Columns: {demo_pedi_raw_2.columns}\n'

#Step 09: Remove all the NA_VAL that has missing values in age and age_cod
demo_pedi_raw_2_copy = demo_pedi_raw_2.copy()
demo_pedi_raw_2_copy = "module_name".rmNA_VALbins(demo_pedi_raw_2_copy)
na_val_rm_log = f'\nFirst wave of NA_VAL removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_2_copy)} records preserved\n'

#Step 10: If still there are NA_VAL values, disregard them
demo_pedi_raw_2_copy = "module_name".rmNA_VALbins_2(demo_pedi_raw_2_copy)
na_val_rm_log_2 = f'\nSecond wave of NA_VAL removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_2_copy)} records preserved\n'

#Step 11: Apply the min-max scaler
demo_pedi_raw_3 = "module_name".normalizeAges(demo_pedi_raw_2_copy)
age_norm_log = f'\nAges normalized at: {now.format('YYYY-MM-DD HH:mm:ss')} | Columns: {demo_pedi_raw_3.columns}\n'

#Step 12: Remove all gender values that are missing
demo_pedi_raw_4 = "module_name".dropMissingSex(demo_pedi_raw_3)
rm_missing_sex_log = f'\nMissing gender values removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_4)} records preserved\n'

#Step 13: Fix the missing values in the reporter country
demo_pedi_raw_5 = "module_name".getOriginCountry(demo_pedi_raw_4)
fix_country_log = f'\nOrigin country added at: {now.format('YYYY-MM-DD HH:mm:ss')} |  Columns: {demo_pedi_raw_5.columns}\n'

#Step 14: remove all 'Country not specified' values from origin country
demo_pedi_raw_6 = "module_name".rmMissingOrigin(demo_pedi_raw_5)
rm_missing_origin_log = f'\nMissing origin values removed at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_6)} records preserved\n'

#Step 15: Convert lbs values to kg
demo_pedi_raw_7 = "module_name".convLbsToKg(demo_pedi_raw_6)
wt_conv_log = f'\nWeights converted to KG at: {now.format('YYYY-MM-DD HH:mm:ss')} |  Columns: {demo_pedi_raw_7.columns}\n'

#Step 16: Let's remove all weight values that has a wt value but not a wt_cod
demo_pedi_raw_8 = "module_name".wtCheck01(demo_pedi_raw_7)
wtcheck01_log = f'\nWeight Check 01 happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_8)} records preserved\n'

#Step 17: Let's check the validity in weights
demo_pedi_raw_9 = "module_name".findWtOutliers(demo_pedi_raw_8)
wtcheck02_log = f'\nWeight Check 02 (Outliers) happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  Columns: {demo_pedi_raw_9.columns}\n'

#Step 18: Now disregard invalid weights
demo_pedi_raw_10 = "module_name".rmWtOutliers(demo_pedi_raw_9)
wtcheck03_log = f'\nWeight Check 03 (outlier removal) happened at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_raw_8)} records preserved\n'

#Step 19: Only get the necessary columns (Final Transformed layer)
demo_pedi_transformed = "module_name".rmWtOutliers(demo_pedi_raw_10)
final_layer_log = f'\nFinal Transformed Layer selected at: {now.format('YYYY-MM-DD HH:mm:ss')} |  {len(demo_pedi_transformed)} records preserved\n'

#Step 20: Export to csv
export_to_csv = "module_name".exportCSV(demo_pedi_transformed, "Out_Path")
export_msg =  f'\n{export_to_csv} at: {now.format('YYYY-MM-DD HH:mm:ss')}\n'



