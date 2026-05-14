"""
Train all anomaly detection models for Credit Card and IoT datasets
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
import joblib
import pickle
import os

# ============================================================
# CREDIT CARD MODELS
# ============================================================

print("=" * 60)
print("TRAINING CREDIT CARD MODELS")
print("=" * 60)

# Load data
print("\n[1] Loading Credit Card data...")
df_cc = pd.read_csv("data/raw/credit_card/credit_card_transactions.csv")
print(f"    Shape: {df_cc.shape}")

# Preprocess
df_cc['trans_date_trans_time'] = pd.to_datetime(df_cc['trans_date_trans_time'])
df_cc['trans_hour'] = df_cc['trans_date_trans_time'].dt.hour
df_cc['trans_weekday'] = df_cc['trans_date_trans_time'].dt.dayofweek
df_cc['trans_month'] = df_cc['trans_date_trans_time'].dt.month
df_cc['dob'] = pd.to_datetime(df_cc['dob'], errors='coerce')
df_cc['card_holder_age'] = (df_cc['trans_date_trans_time'] - df_cc['dob']).dt.days / 365.25
df_cc['distance'] = np.sqrt((df_cc['lat'] - df_cc['merch_lat'])**2 + (df_cc['long'] - df_cc['merch_long'])**2)

# Features for ML model
ml_features = ['amt', 'city_pop', 'card_holder_age', 'trans_hour', 'trans_weekday', 'trans_month', 'distance']
X = df_cc[ml_features].fillna(0)

# Split for evaluation
y_true = df_cc['is_fraud'].values

X_train, X_test, y_train, y_test = train_test_split(X, y_true, test_size=0.2, random_state=42, stratify=y_true)
print(f"    Train: {len(X_train)}, Test: {len(X_test)}")

# --- Model 1: Isolation Forest ---
print("\n[2] Training Isolation Forest (ML Model)...")
iso_model = IsolationForest(
    n_estimators=400,
    contamination=0.01,
    max_samples=512,
    max_features=0.8,
    bootstrap=False,
    random_state=42,
    n_jobs=-1
)
iso_model.fit(X_train)

# Predict
y_pred = iso_model.predict(X_test)
y_pred = (y_pred == -1).astype(int)
f1_iso = f1_score(y_test, y_pred)
print(f"    F1 Score: {f1_iso:.4f}")

# Save scaler + model
scaler_cc = StandardScaler()
scaler_cc.fit(X_train)
joblib.dump(iso_model, "models/isolation_forest_credit_card.pkl")
joblib.dump(scaler_cc, "models/scaler_credit_card.pkl")
joblib.dump(ml_features, "models/cc_ml_features.pkl")
print("    Saved: models/isolation_forest_credit_card.pkl")

# --- Model 2: Statistical Method (Z-score threshold) ---
print("\n[3] Training Statistical Method (Z-score)...")
stat_features = ['amt', 'distance', 'city_pop']
X_stat = df_cc[stat_features].fillna(0)

# Calculate z-scores
mean_vals = X_stat.mean()
std_vals = X_stat.std()
combined_zscore = ((X_stat - mean_vals) / (std_vals + 1e-10)).abs().max(axis=1)

# Find optimal threshold
thresholds = np.percentile(combined_zscore, np.arange(90, 99.5, 0.5))
best_f1 = 0
best_t = 0
for t in thresholds:
    y_pred_t = (combined_zscore > t).astype(int)
    f1 = f1_score(y_true, y_pred_t)
    if f1 > best_f1:
        best_f1 = f1
        best_t = t

print(f"    Optimal threshold: {best_t:.4f}")
print(f"    Best F1 Score: {best_f1:.4f}")

# Save statistical model
stat_bundle = {
    "threshold": best_t,
    "best_f1": best_f1,
    "mean": mean_vals.to_dict(),
    "std": std_vals.to_dict(),
    "features": stat_features,
    "method": "zscore"
}
with open("models/statistical_credit_card.pkl", "wb") as f:
    pickle.dump(stat_bundle, f)
print("    Saved: models/statistical_credit_card.pkl")

# ============================================================
# IOT MODELS
# ============================================================

print("\n" + "=" * 60)
print("TRAINING IOT MODELS")
print("=" * 60)

# Load data
print("\n[4] Loading IoT data...")
df_iot = pd.read_csv("data/raw/iot/iot.csv")
print(f"    Shape: {df_iot.shape}")

# Features
numeric_cols = df_iot.select_dtypes(include=[np.number]).columns.tolist()
X_iot = df_iot[numeric_cols].fillna(0)
y_iot = df_iot['label'].values if 'label' in df_iot.columns else np.zeros(len(df_iot))

X_train_iot, X_test_iot, y_train_iot, y_test_iot = train_test_split(
    X_iot, y_iot, test_size=0.2, random_state=42
)

# --- Model 3: Isolation Forest for IoT ---
print("\n[5] Training Isolation Forest (IoT)...")
iso_iot = IsolationForest(
    n_estimators=200,
    contamination=0.1,
    random_state=42,
    n_jobs=-1
)
iso_iot.fit(X_train_iot)

y_pred_iot = iso_iot.predict(X_test_iot)
y_pred_iot = (y_pred_iot == -1).astype(int)
if len(np.unique(y_test_iot)) > 1:
    f1_iot = f1_score(y_test_iot, y_pred_iot)
    print(f"    F1 Score: {f1_iot:.4f}")

# Save
scaler_iot = StandardScaler()
scaler_iot.fit(X_train_iot)
joblib.dump(iso_iot, "models/isolation_forest_iot.pkl")
joblib.dump(scaler_iot, "models/scaler_iot.pkl")
joblib.dump(numeric_cols, "models/iot_ml_features.pkl")
print("    Saved: models/isolation_forest_iot.pkl")

# --- Model 4: Statistical Method for IoT ---
print("\n[6] Training Statistical Method (IoT)...")
# Use IQR-based detection
stat_cols_iot = numeric_cols[:min(5, len(numeric_cols))]
X_stat_iot = df_iot[stat_cols_iot].fillna(0)

# Calculate IQR bounds
q1 = X_stat_iot.quantile(0.25)
q3 = X_stat_iot.quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

# Count outliers per row
outlier_count = ((X_stat_iot < lower_bound) | (X_stat_iot > upper_bound)).sum(axis=1)
# Threshold = number of features that are outliers
stat_threshold = len(stat_cols_iot) * 0.3

stat_bundle_iot = {
    "q1": q1.to_dict(),
    "q3": q3.to_dict(),
    "iqr": iqr.to_dict(),
    "lower_bound": lower_bound.to_dict(),
    "upper_bound": upper_bound.to_dict(),
    "threshold": stat_threshold,
    "features": stat_cols_iot,
    "method": "iqr"
}
with open("models/statistical_iot.pkl", "wb") as f:
    pickle.dump(stat_bundle_iot, f)
print("    Saved: models/statistical_iot.pkl")

print("\n" + "=" * 60)
print("ALL MODELS TRAINED SUCCESSFULLY!")
print("=" * 60)
print("\nModels saved to 'models/' directory:")
print("  - isolation_forest_credit_card.pkl")
print("  - statistical_credit_card.pkl")
print("  - isolation_forest_iot.pkl")
print("  - statistical_iot.pkl")
print("  - scaler_credit_card.pkl")
print("  - scaler_iot.pkl")
