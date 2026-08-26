"""
Train baseline 4-Tier Document Sensitivity Classifier for SecureFlow AI.

Classifies documents into:
  - Highly Confidential
  - Confidential
  - Internal
  - Public
"""

import os
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import joblib

DATA_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = DATA_DIR / "processed" / "document_classification"
MODEL_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "models"


def main():
    train_path = PROCESSED_DIR / "train.csv"
    val_path = PROCESSED_DIR / "validation.csv"
    test_path = PROCESSED_DIR / "test.csv"

    if not train_path.exists():
        print(f"[ERROR] Processed data not found at {train_path}. Please run organize_datasets.py first.")
        return

    print("=" * 60)
    print(" SecureFlow AI — 4-Tier Document Classifier Training")
    print("=" * 60)

    # 1. Load data
    print(f"Loading data from {PROCESSED_DIR}...")
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)

    print(f"Train samples: {len(train_df)} | Val samples: {len(val_df)} | Test samples: {len(test_df)}")

    # 2. Build Pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ])

    # 3. Fit
    print("Training classifier...")
    pipeline.fit(train_df["cleaned_text"].fillna(train_df["text"]), train_df["label"])

    # 4. Evaluate on Validation Set
    print("\n--- Validation Set Performance ---")
    val_preds = pipeline.predict(val_df["cleaned_text"].fillna(val_df["text"]))
    print(classification_report(val_df["label"], val_preds))

    # 5. Evaluate on Test Set
    print("\n--- Test Set Performance ---")
    test_preds = pipeline.predict(test_df["cleaned_text"].fillna(test_df["text"]))
    print(classification_report(test_df["label"], test_preds))

    # 6. Save Model
    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model_file = MODEL_OUTPUT_DIR / "document_classifier_baseline.joblib"
    joblib.dump(pipeline, model_file)
    print(f"\n[SUCCESS] Model saved to {model_file}")


if __name__ == "__main__":
    main()
