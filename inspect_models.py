import joblib
import numpy as np
import sys
import pandas as pd

# Paths
SCALER_PATH = r"d:\Dev_Drive\Coding Project Files\Uni_Assignment\UAS\36230035_KeamananData_UAS\src\models_dev\models\scaler.joblib"
MODEL_PATH = r"d:\Dev_Drive\Coding Project Files\Uni_Assignment\UAS\36230035_KeamananData_UAS\src\models_dev\models\xgboost.joblib"

def inspect_artifacts():
    print(f"Loading Scaler from: {SCALER_PATH}")
    try:
        scaler = joblib.load(SCALER_PATH)
        print(f"Scaler Type: {type(scaler)}")
        if hasattr(scaler, 'n_features_in_'):
            print(f"Scaler Expected Features: {scaler.n_features_in_}")
        
        if hasattr(scaler, 'feature_names_in_'):
            features = list(scaler.feature_names_in_)
            with open("feature_list.txt", "w") as f:
                f.write("\n".join(features))
            print("Feature names saved to feature_list.txt")
        else:
            print("Scaler does not store feature names.")
            
    except Exception as e:
        print(f"Error loading scaler: {e}")

if __name__ == "__main__":
    inspect_artifacts()
