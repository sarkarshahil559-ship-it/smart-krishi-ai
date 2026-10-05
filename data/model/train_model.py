import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
data = pd.read_csv("../crop_data.csv")

# Input features
X = data[
    [
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall"
    ]
]

# Target
y = data["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)

print("================================")
print("🌱 SMART KRISHI AI")
print("================================")
print("Model trained successfully! 🤖")
print("Model Accuracy:", accuracy)

# Save model
with open("crop_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model saved successfully! 🌾")
print("================================")