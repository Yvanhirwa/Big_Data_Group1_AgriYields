# dashboard/ml/train_model.py
import pickle
import os
from sklearn.linear_model import LinearRegression

MODEL_PATH = os.path.join(os.path.dirname(__file__), "linreg_model.pkl")

def train_and_save(training_df):
    # training_df expected to have columns: Temperature, Rainfall, SoilMoisture, Yield
    X = training_df[["Temperature", "Rainfall", "SoilMoisture"]]
    y = training_df["Yield"]
    model = LinearRegression()
    model.fit(X, y)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    return MODEL_PATH

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None
