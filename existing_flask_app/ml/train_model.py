import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load training data
data = pd.read_csv("training_data_v2.csv")

X = data["query"]
y = data["category"]

# Create ML Pipeline
model = Pipeline([

    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    )

])

# Train Model
model.fit(X, y)

# Save Model
joblib.dump(model, "healthcare_model.pkl")

print("======================================")
print(" AI Healthcare Model Trained Successfully ")
print("======================================")
print(f"Training Records : {len(data)}")
print(f"Categories       : {len(data['category'].unique())}")
print("Algorithm        : Logistic Regression")
print("Vectorizer       : TF-IDF (1-gram + 2-gram)")
print("======================================")