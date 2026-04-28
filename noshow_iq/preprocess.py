import pandas as pd

def load_and_clean(filepath):
    df = pd.read_csv(filepath)

    # Fix the dangerous column name — hyphen breaks code
    df.rename(columns={"No-show": "no_show"}, inplace=True)

    # Standardize all column names to lowercase with underscores
    df.columns = df.columns.str.lower().str.replace("-", "_")

    # The target: "Yes" means they DID no-show. Convert to 1/0.
    df["no_show"] = (df["no_show"] == "Yes").astype(int)

    # Remove impossible ages (negative or over 115)
    df = df[(df["age"] >= 0) & (df["age"] <= 115)]

    # Parse dates — they're stored as strings
    df["scheduledday"] = pd.to_datetime(df["scheduledday"])
    df["appointmentday"] = pd.to_datetime(df["appointmentday"])

    # Feature 1: days booked in advance (required by exam)
    df["days_in_advance"] = (
        df["appointmentday"] - df["scheduledday"]
    ).dt.days.clip(lower=0)  # negative means same-day, treat as 0

    # Feature 2: day of week the appointment falls on
    df["appointment_weekday"] = df["appointmentday"].dt.dayofweek

    return df


def get_features_and_target(df):
    feature_cols = [
        "age", "scholarship", "hipertension", "diabetes",
        "alcoholism", "handcap", "sms_received",
        "days_in_advance", "appointment_weekday"
    ]
    X = df[feature_cols]
    y = df["no_show"]
    return X, y
