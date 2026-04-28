import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE  # handles class imbalance


MODEL_PATH = "noshow_model.joblib"


def train(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # SMOTE creates synthetic minority (no-show) samples so
    # the model doesn't just learn to always predict "shows up"
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train_res, y_train_res)

    joblib.dump(clf, MODEL_PATH)
    return clf, X_test, y_test


def evaluate(clf, X_test, y_test):
    y_pred = clf.predict(X_test)
    # classification_report shows precision/recall/F1 for BOTH classes
    report = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))
    return report


def predict(features: dict):
    clf = joblib.load(MODEL_PATH)
    import pandas as pd
    X = pd.DataFrame([features])
    prob = clf.predict_proba(X)[0][1]  # probability of no-show
    risk = "high" if prob > 0.5 else "low"
    rec = (
        "Send reminder and call patient"
        if risk == "high"
        else "Standard reminder sufficient"
    )
    return {"risk_level": risk, "probability": round(float(prob), 4),
            "recommendation": rec}