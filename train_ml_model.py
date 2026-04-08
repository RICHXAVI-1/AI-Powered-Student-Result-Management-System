"""
ML Model Trainer for Student Performance Prediction
Run this AFTER generate_training_data.py:  python train_ml_model.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (classification_report, accuracy_score,
                             confusion_matrix, roc_auc_score)
from sklearn.pipeline import Pipeline

TRAINING_CSV   = 'ml_data/student_training_data.csv'
MODEL_DIR      = 'ml_data'
MODEL_PATH     = os.path.join(MODEL_DIR, 'performance_model.pkl')
SCALER_PATH    = os.path.join(MODEL_DIR, 'scaler.pkl')
ENCODER_PATH   = os.path.join(MODEL_DIR, 'label_encoder.pkl')
FEATURE_PATH   = os.path.join(MODEL_DIR, 'feature_names.pkl')

FEATURE_COLS = [
    'avg_score', 'prev_avg_score', 'score_trend', 'score_std',
    'failed_courses', 'gpa', 'pass_rate',
    'attendance_rate', 'study_hours_per_week', 'num_courses'
]

TARGET_COL = 'performance_label'


def train():
    print("📂 Loading training data...")
    df = pd.read_csv(TRAINING_CSV)
    print(f"   Records: {len(df)}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    print(f"   Classes: {list(le.classes_)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)

    # Scale features
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # --- Train Random Forest (primary model) ---
    print("\n🌲 Training Random Forest Classifier...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_s, y_train)

    # Cross-validation
    cv_scores = cross_val_score(rf, X_train_s, y_train, cv=5, scoring='accuracy')
    print(f"   CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Test evaluation
    y_pred = rf.predict(X_test_s)
    acc = accuracy_score(y_test, y_pred)
    print(f"   Test Accuracy: {acc:.4f}")
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Feature importance
    importances = pd.Series(rf.feature_importances_, index=FEATURE_COLS)
    print("\n   Feature Importances:")
    for feat, imp in importances.sort_values(ascending=False).items():
        print(f"     {feat:30s}: {imp:.4f}")

    # --- Save artefacts ---
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH,   'wb') as f: pickle.dump(rf, f)
    with open(SCALER_PATH,  'wb') as f: pickle.dump(scaler, f)
    with open(ENCODER_PATH, 'wb') as f: pickle.dump(le, f)
    with open(FEATURE_PATH, 'wb') as f: pickle.dump(FEATURE_COLS, f)

    print(f"\n✅ Model saved → {MODEL_PATH}")
    print(f"✅ Scaler saved → {SCALER_PATH}")
    print(f"✅ Encoder saved → {ENCODER_PATH}")

    return acc


if __name__ == '__main__':
    train()
