import joblib
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any

class ModelLoader:
    def __init__(self, model_path: str, scaler_path: str):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.is_loaded = False
        
        # Threat Mapping
        self.class_map = {
            0: "Benign",
            1: "Brute Force",
            2: "DDoS",
            3: "Other"
        }
        
        self.threat_info = {
            "Benign": {
                "Tipe Ancaman": "Normal Traffic",
                "Mode Respon": "Monitoring",
                "Aksi Mitigasi": ["None. Traffic is safe."]
            },
            "Brute Force": {
                "Tipe Ancaman": "Credential Access",
                "Mode Respon": "Block Source IP",
                "Aksi Mitigasi": [
                    "Block Source IP immediately",
                    "Reset affected user passwords",
                    "Enable 2FA enforcement"
                ]
            },
            "DDoS": {
                "Tipe Ancaman": "Denial of Service",
                "Mode Respon": "Rate Limiting",
                "Aksi Mitigasi": [
                    "Activate Rate Limiting on API Gateway",
                    "Route traffic through scrubbing center",
                    "Block UDP fragments"
                ]
            },
            "Other": {
                "Tipe Ancaman": "Malware / Botnet",
                "Mode Respon": "Deep Packet Inspection",
                "Aksi Mitigasi": [
                    "Isolate infected host",
                    "Analyzing payload signature",
                    "Update firewall rules"
                ]
            }
        }
        
        self._load_artifacts()

    def _load_artifacts(self):
        """Internal method to load model and scaler."""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at: {self.model_path}")
            if not os.path.exists(self.scaler_path):
                raise FileNotFoundError(f"Scaler file not found at: {self.scaler_path}")
                
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            
            # Load features from scaler if available
            if hasattr(self.scaler, 'feature_names_in_'):
                self.feature_names = list(self.scaler.feature_names_in_)
            else:
                self.feature_names = [f"f{i}" for i in range(self.scaler.n_features_in_)]
            
            self.is_loaded = True
            print(f"[INFO] Model and Scaler loaded successfully.\nModel: {self.model_path}\nScaler: {self.scaler_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load artifacts: {e}")
            self.is_loaded = False
            raise e

    def predict(self, input_features: list) -> Dict[str, Any]:
        """
        Melakukan prediksi dari data raw input.
        - Scaling data using DataFrame to match feature names
        - Prediksi model
        - Mapping hasil ke informasi mitigasi
        """
        if not self.is_loaded:
            raise RuntimeError("Model or Scaler is not loaded.")

        try:
            # 1. Convert to DataFrame to match Scaler's expected feature names
            # Expected shape: (1, 69)
            raw_df = pd.DataFrame([input_features], columns=self.feature_names)
            
            # 2. Scaling
            scaled_data = self.scaler.transform(raw_df)
            
            # 3. Predict
            prediction_idx = self.model.predict(scaled_data)[0]
            prediction_label = self.class_map.get(prediction_idx, "Unknown")
            
            # 4. Get Proba (Optional)
            try:
                proba = self.model.predict_proba(scaled_data)[0]
                confidence = float(np.max(proba))
            except:
                confidence = 1.0 # Fallback
                
            # 5. Construct Result
            mitigation = self.threat_info.get(prediction_label, {})
            
            result = {
                "prediction_class": prediction_label,
                "prediction_id": int(prediction_idx),
                "confidence": confidence,
                "threat_type": mitigation.get("Tipe Ancaman", "Unknown"),
                "response_mode": mitigation.get("Mode Respon", "Manual"),
                "mitigation_actions": mitigation.get("Aksi Mitigasi", []),
                "input_summary": f"Proto: {input_features[0]}, Flow: {input_features[1]:.0f}"
            }
            
            return result
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            raise e

# Singleton Pattern for Global Loader
_loader = None

def get_model_loader():
    global _loader
    if _loader is None:
        # Paths relative to project root (assuming main.py is run from root)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Go up one level from src/app to src, then to models_dev
        ROOT_SRC = os.path.dirname(BASE_DIR) 
        
        MODEL_PATH = r"d:\Dev_Drive\Coding Project Files\Uni_Assignment\UAS\36230035_KeamananData_UAS\src\models_dev\models\xgboost.joblib"
        SCALER_PATH = r"d:\Dev_Drive\Coding Project Files\Uni_Assignment\UAS\36230035_KeamananData_UAS\src\models_dev\models\scaler.joblib"
        
        _loader = ModelLoader(MODEL_PATH, SCALER_PATH)
    return _loader
