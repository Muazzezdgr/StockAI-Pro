"""
utils/model_utils.py  –  LSTM + Random Forest eğitim & değerlendirme
"""
import numpy as np, pickle, os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score, roc_curve)

def train_random_forest(X_train, y_train, n_estimators=200, max_depth=8):
    model = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth,
        min_samples_split=10, min_samples_leaf=5,
        max_features="sqrt", class_weight="balanced",
        random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    return model

def build_lstm_model(input_shape):
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Bidirectional
        from tensorflow.keras.optimizers import Adam
        model = Sequential([
            Bidirectional(LSTM(128, return_sequences=True), input_shape=input_shape),
            BatchNormalization(), Dropout(0.3),
            LSTM(64, return_sequences=True),
            BatchNormalization(), Dropout(0.3),
            LSTM(32, return_sequences=False),
            BatchNormalization(), Dropout(0.2),
            Dense(64, activation="relu"), Dropout(0.2),
            Dense(32, activation="relu"),
            Dense(1, activation="sigmoid")
        ])
        model.compile(optimizer=Adam(0.001), loss="binary_crossentropy", metrics=["accuracy"])
        return model
    except ImportError:
        return None

def train_lstm(X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
    try:
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
        model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
        if model is None: return None, []
        callbacks = [
            EarlyStopping(patience=8, restore_best_weights=True),
            ReduceLROnPlateau(factor=0.5, patience=4, min_lr=1e-6)
        ]
        history = model.fit(X_train, y_train, validation_data=(X_val, y_val),
                            epochs=epochs, batch_size=batch_size,
                            callbacks=callbacks, verbose=0)
        return model, history.history
    except Exception as e:
        print(f"LSTM hata: {e}"); return None, []

def evaluate_model(model, X_test, y_test, model_type="rf"):
    if model is None: return {}
    try:
        if model_type == "lstm":
            y_prob = model.predict(X_test, verbose=0).flatten()
            y_pred = (y_prob > 0.5).astype(int)
        else:
            y_prob = model.predict_proba(X_test)[:, 1]
            y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0.5
        cm  = confusion_matrix(y_test, y_pred)
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        return {"accuracy": acc, "auc": auc, "confusion_matrix": cm,
                "report": classification_report(y_test, y_pred, output_dict=True),
                "y_pred": y_pred, "y_prob": y_prob, "roc_fpr": fpr, "roc_tpr": tpr}
    except Exception as e:
        print(f"Değerlendirme hatası: {e}"); return {}

def get_feature_importance(model, feature_names):
    try:
        imp = model.feature_importances_
        return sorted(zip(feature_names, imp), key=lambda x: x[1], reverse=True)
    except: return []

def save_models(rf_model, scaler, path="models/"):
    os.makedirs(path, exist_ok=True)
    pickle.dump(rf_model, open(f"{path}rf_model.pkl","wb"))
    pickle.dump(scaler,   open(f"{path}scaler.pkl","wb"))

def load_models(path="models/"):
    try:
        rf     = pickle.load(open(f"{path}rf_model.pkl","rb"))
        scaler = pickle.load(open(f"{path}scaler.pkl","rb"))
        return rf, scaler
    except: return None, None
