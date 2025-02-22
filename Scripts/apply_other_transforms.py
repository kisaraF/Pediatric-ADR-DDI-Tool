import pandas as pd
import glob
import os
import other_transforms 

reactions_fp = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\RAW_DATA\\REACTIONS'
outcomes_fp = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Data\\RAW_DATA\\OUTCOMES'

#Import Reactions
reactions_df = other_transforms.importFile(reactions_fp)
