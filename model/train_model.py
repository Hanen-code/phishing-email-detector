"""
train_model.py
----------------
Trains a phishing email classifier using TF-IDF features and compares
several classical ML models (Logistic Regression, Multinomial Naive Bayes,
Linear SVM). The best-performing model (by F1-score) is saved together
with the fitted TF-IDF vectorizer into model.pkl for use by the FastAPI
backend.

Usage:
    python train_model.py
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"

RANDOM_STATE = 42


def load_data():
    """Load the dataset.csv file containing 'text' and 'label' columns."""
    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)
    return df


def evaluate(model, X_test, y_test, name):
    """Print evaluation metrics for a trained model and return its F1 score."""
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, pos_label="phishing")
    rec = recall_score(y_test, y_pred, pos_label="phishing")
    f1 = f1_score(y_test, y_pred, pos_label="phishing")

    print(f"\n=== {name} ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(classification_report(y_test, y_pred))

    return f1


def main():
    print("Loading dataset...")
    df = load_data()
    print(f"Total samples: {len(df)}")
    print(df["label"].value_counts())

    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # --- Feature extraction ---
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_df=0.95,
        min_df=1,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # --- Train and compare multiple models ---
    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Multinomial Naive Bayes": MultinomialNB(),
        "Linear SVM": LinearSVC(random_state=RANDOM_STATE),
    }

    results = {}
    trained_models = {}

    for name, model in candidates.items():
        model.fit(X_train_vec, y_train)
        f1 = evaluate(model, X_test_vec, y_test, name)
        results[name] = f1
        trained_models[name] = model

    # --- Pick the best model based on F1-score ---
    best_name = max(results, key=results.get)
    best_model = trained_models[best_name]
    print(f"\n>>> Best model: {best_name} (F1-score = {results[best_name]:.4f})")

    # --- Save vectorizer + model together ---
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({
            "vectorizer": vectorizer,
            "model": best_model,
            "model_name": best_name,
        }, f)

    print(f"\nModel and vectorizer saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
