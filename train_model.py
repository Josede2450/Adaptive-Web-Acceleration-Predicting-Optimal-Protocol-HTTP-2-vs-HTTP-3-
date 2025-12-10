import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import warnings

# Suppress all warnings for clean output
warnings.filterwarnings("ignore")

# Load the processed dataset
df = pd.read_csv("dataset_ready.csv")

# Encode the better_protocol column numerically for ML
df["better_protocol_code"] = df["better_protocol"].map({"HTTP/2": 0, "HTTP/3": 1})

# Use only latency as input feature
X = df[["latency"]]
y = df["better_protocol_code"]

# Handle very small datasets safely
if len(df) < 3:
    print("Not enough data to split. Training on full dataset...")
    X_train, X_test, y_train, y_test = X, X, y, y
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )

# Train the Decision Tree model
model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

# Evaluate accuracy safely
if len(y_test) > 0:
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
else:
    accuracy = 1.0  

# Show training summary
print(f"Model trained successfully with accuracy: {accuracy * 100:.2f}%")

# Save model
joblib.dump(model, "protocol_predictor.pkl")
print("Model saved as 'protocol_predictor.pkl'")
