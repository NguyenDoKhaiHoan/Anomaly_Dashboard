"""
Train anomaly detection models on RAW (non-preprocessed) data
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
    classification_report, confusion_matrix
)
import joblib
import pickle
import os
from time import time

os.makedirs("models", exist_ok=True)

# ============================================================
# CREDIT CARD - RAW DATA
# ============================================================

print("=" * 70)
print("CREDIT CARD - RAW DATA (NO PREPROCESSING)")
print("=" * 70)

t0 = time()

# Load raw data
print("\n[1] Loading raw Credit Card data...")
df_cc = pd.read_csv("data/raw/credit_card/credit_card_transactions.csv")
print(f"    Shape: {df_cc.shape}")
print(f"    Columns: {list(df_cc.columns)}")

# Use only numeric columns directly
numeric_cols_cc = df_cc.select_dtypes(include=[np.number]).columns.tolist()
print(f"    Numeric columns: {numeric_cols_cc}")

X_cc = df_cc[numeric_cols_cc].fillna(0)
y_cc = df_cc['is_fraud'].values if 'is_fraud' in df_cc.columns else np.zeros(len(df_cc))
print(f"    X shape: {X_cc.shape}, y distribution: {np.bincount(y_cc.astype(int))}")

X_train, X_test, y_train, y_test = train_test_split(
    X_cc, y_cc, test_size=0.2, random_state=42, stratify=y_cc
)

# --- Model 1: Isolation Forest (Raw) ---
print("\n[2] Training Isolation Forest on raw data...")
scaler_cc = StandardScaler()
X_train_scaled = scaler_cc.fit_transform(X_train)
X_test_scaled = scaler_cc.transform(X_test)

iso_cc = IsolationForest(
    n_estimators=100,
    contamination=0.02,
    random_state=42,
    n_jobs=-1
)
iso_cc.fit(X_train_scaled)

y_pred_iso = iso_cc.predict(X_test_scaled)
y_pred_iso = (y_pred_iso == -1).astype(int)
y_score_iso = -iso_cc.decision_function(X_test_scaled)

print("\n" + "-" * 50)
print("ISOLATION FOREST (Credit Card - Raw)")
print("-" * 50)
print(f"F1 Score:  {f1_score(y_test, y_pred_iso):.4f}")
print(f"Precision: {precision_score(y_test, y_pred_iso):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred_iso):.4f}")
print(f"ROC-AUC:   {roc_auc_score(y_test, y_score_iso):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred_iso))

# Save
joblib.dump(iso_cc, "models/cc_iso_raw.pkl")
joblib.dump(scaler_cc, "models/cc_scaler_raw.pkl")
print("\n    Saved: models/cc_iso_raw.pkl")

# --- Model 2: Statistical Method (Raw - Z-score) ---
print("\n[3] Training Statistical Method on raw data...")

# Calculate z-scores for all numeric features
mean_raw = X_cc.mean()
std_raw = X_cc.std()
combined_zscore = ((X_cc - mean_raw) / (std_raw + 1e-10)).abs().max(axis=1)

# Find optimal threshold using F1
thresholds = np.percentile(combined_zscore, np.arange(90, 99.9, 0.1))
best_f1_stat, best_t_stat = 0, 0
for t in thresholds:
    y_pred_t = (combined_zscore > t).astype(int)
    f1 = f1_score(y_cc, y_pred_t)
    if f1 > best_f1_stat:
        best_f1_stat = f1
        best_t_stat = t

y_pred_stat = (combined_zscore > best_t_stat).astype(int)

# Split for evaluation
y_train_stat = y_pred_stat[:len(X_train)]
y_test_stat = y_pred_stat[len(X_train):]

print("\n" + "-" * 50)
print("STATISTICAL METHOD - Z-SCORE (Credit Card - Raw)")
print("-" * 50)
print(f"Optimal Threshold: {best_t_stat:.4f}")
print(f"F1 Score:  {f1_score(y_cc[len(X_train):], y_test_stat):.4f}")
print(f"Precision: {precision_score(y_cc[len(X_train):], y_test_stat):.4f}")
print(f"Recall:    {recall_score(y_cc[len(X_train):], y_test_stat):.4f}")

stat_bundle_cc = {
    "threshold": best_t_stat,
    "mean": mean_raw.to_dict(),
    "std": std_raw.to_dict(),
    "features": list(X_cc.columns),
    "method": "zscore_max"
}
with open("models/cc_statistical_raw.pkl", "wb") as f:
    pickle.dump(stat_bundle_cc, f)
print("\n    Saved: models/cc_statistical_raw.pkl")

print(f"\n    Credit Card training time: {time()-t0:.2f}s")

# ============================================================
# IOT - RAW DATA
# ============================================================

print("\n" + "=" * 70)
print("IOT - RAW DATA (NO PREPROCESSING)")
print("=" * 70)

t1 = time()

# Load raw data
print("\n[4] Loading raw IoT data...")
df_iot = pd.read_csv("data/raw/iot/iot.csv")
print(f"    Shape: {df_iot.shape}")
print(f"    Columns: {list(df_iot.columns)}")

numeric_cols_iot = df_iot.select_dtypes(include=[np.number]).columns.tolist()
print(f"    Numeric columns: {numeric_cols_iot}")

X_iot = df_iot[numeric_cols_iot].fillna(0)
y_iot = df_iot['label'].values if 'label' in df_iot.columns else np.zeros(len(df_iot))
print(f"    X shape: {X_iot.shape}")
if 'label' in df_iot.columns:
    print(f"    Label distribution: {np.bincount(y_iot.astype(int))}")

X_train_iot, X_test_iot, y_train_iot, y_test_iot = train_test_split(
    X_iot, y_iot, test_size=0.2, random_state=42
)

# --- Model 3: Isolation Forest (IoT - Raw) ---
print("\n[5] Training Isolation Forest on raw IoT data...")
scaler_iot = StandardScaler()
X_train_iot_scaled = scaler_iot.fit_transform(X_train_iot)
X_test_iot_scaled = scaler_iot.transform(X_test_iot)

iso_iot = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=42,
    n_jobs=-1
)
iso_iot.fit(X_train_iot_scaled)

y_pred_iot = iso_iot.predict(X_test_iot_scaled)
y_pred_iot = (y_pred_iot == -1).astype(int)
y_score_iot = -iso_iot.decision_function(X_test_iot_scaled)

print("\n" + "-" * 50)
print("ISOLATION FOREST (IoT - Raw)")
print("-" * 50)
print(f"F1 Score:  {f1_score(y_test_iot, y_pred_iot):.4f}")
print(f"Precision: {precision_score(y_test_iot, y_pred_iot):.4f}")
print(f"Recall:    {recall_score(y_test_iot, y_pred_iot):.4f}")
if len(np.unique(y_test_iot)) > 1:
    print(f"ROC-AUC:   {roc_auc_score(y_test_iot, y_score_iot):.4f}")
print("\nConfusion Matrix:")
print(confusion_matrix(y_test_iot, y_pred_iot))

joblib.dump(iso_iot, "models/iot_iso_raw.pkl")
joblib.dump(scaler_iot, "models/iot_scaler_raw.pkl")
print("\n    Saved: models/iot_iso_raw.pkl")

# --- Model 4: Statistical Method (IoT - Raw - IQR) ---
print("\n[6] Training Statistical Method on raw IoT data...")

q1_iot = X_iot.quantile(0.25)
q3_iot = X_iot.quantile(0.75)
iqr_iot = q3_iot - q1_iot
lower = q1_iot - 1.5 * iqr_iot
upper = q3_iot + 1.5 * iqr_iot

# Count how many features are outliers per row
outlier_flags = ((X_iot < lower) | (X_iot > upper)).sum(axis=1)
outlier_ratio = outlier_flags / len(X_iot.columns)

# Try different thresholds
thresholds_iot = np.arange(0.1, 0.9, 0.05)
best_f1_iot_stat, best_t_iot = 0, 0.5
for t in thresholds_iot:
    y_pred_t = (outlier_ratio > t).astype(int)
    f1 = f1_score(y_iot, y_pred_t)
    if f1 > best_f1_iot_stat:
        best_f1_iot_stat = f1
        best_t_iot = t

y_pred_iot_stat = (outlier_ratio > best_t_iot).astype(int)

print("\n" + "-" * 50)
print("STATISTICAL METHOD - IQR (IoT - Raw)")
print("-" * 50)
print(f"Optimal Outlier Ratio Threshold: {best_t_iot:.2f}")
print(f"F1 Score:  {f1_score(y_iot, y_pred_iot_stat):.4f}")
print(f"Precision: {precision_score(y_iot, y_pred_iot_stat):.4f}")
print(f"Recall:    {recall_score(y_iot, y_pred_iot_stat):.4f}")

stat_bundle_iot = {
    "q1": q1_iot.to_dict(),
    "q3": q3_iot.to_dict(),
    "iqr": iqr_iot.to_dict(),
    "lower_bound": lower.to_dict(),
    "upper_bound": upper.to_dict(),
    "threshold": best_t_iot,
    "features": list(X_iot.columns),
    "method": "iqr_count"
}
with open("models/iot_statistical_raw.pkl", "wb") as f:
    pickle.dump(stat_bundle_iot, f)
print("\n    Saved: models/iot_statistical_raw.pkl")

print(f"\n    IoT training time: {time()-t1:.2f}s")

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY - MODELS TRAINED ON RAW DATA")
print("=" * 70)
print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│ CREDIT CARD DATASET                                                 │
├─────────────────────────────────────────────────────────────────────┤
│ Model                  │ File                    │ F1 Score         │
├─────────────────────────────────────────────────────────────────────┤
│ Isolation Forest       │ cc_iso_raw.pkl          │ {f1_score(y_test, y_pred_iso):.4f}            │
│ Statistical (Z-score)  │ cc_statistical_raw.pkl  │ {best_f1_stat:.4f}            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ IOT DATASET                                                         │
├─────────────────────────────────────────────────────────────────────┤
│ Model                  │ File                    │ F1 Score         │
├─────────────────────────────────────────────────────────────────────┤
│ Isolation Forest       │ iot_iso_raw.pkl         │ {f1_score(y_test_iot, y_pred_iot):.4f}            │
│ Statistical (IQR)      │ iot_statistical_raw.pkl  │ {best_f1_iot_stat:.4f}            │
└─────────────────────────────────────────────────────────────────────┘
""")
print(f"\nTotal time: {time()-t0:.2f}s")
print("\nAll models saved to 'models/' directory!")
