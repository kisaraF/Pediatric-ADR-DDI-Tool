import pandas as pd
import pickle 

model_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\Scripts\\Demographic Scripts\\demog_wt_model/rf_all.pkl'

def getModel():
    with open(model_path, "rb") as f:
        gbr_model = pickle.load(f)
        return gbr_model