import pandas as pd
import pickle 

model_1_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Scripts\\Demographic Scripts\\demog_wt_model/rf_age_grp_1.pkl'
model_2_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Scripts\\Demographic Scripts\\demog_wt_model/rf_age_grp_2.pkl'
model_3_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Scripts\\Demographic Scripts\\demog_wt_model/rf_age_grp_3.pkl'

def getModel_1():
    with open(model_1_path, "rb") as f:
        rf_mod_1 = pickle.load(f)
        return rf_mod_1

def getModel_2():
    with open(model_2_path, "rb") as f:
        rf_mod_2 = pickle.load(f)
        return rf_mod_2
    
def getModel_3():
    with open(model_3_path, "rb") as f:
        rf_mod_3 = pickle.load(f)
        return rf_mod_3