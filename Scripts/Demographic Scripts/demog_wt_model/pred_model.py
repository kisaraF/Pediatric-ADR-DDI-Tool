import pandas as pd
import pickle 

model_path = 'C:\\Users\\USER\\Desktop\\FYP\\fyp-sandbox-2\\demog_wt_model/xgboost_model.pkl'

def getModel():
    with open(model_path, "rb") as f:
        xgb_model = pickle.load(f)
        return xgb_model