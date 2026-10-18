
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

data=pd.read_csv("gesture_data.csv")

X=data.drop(columns=["label"])
y=data["label"]

print("Gesture sample counts:")
print(y.value_counts())

X_train,X_test,y_train,y_test=train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model=RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train,y_train)

predictions=model.predict(X_test)

accuracy=accuracy_score(y_test,predictions)

print("\nModel training completed!")
print("Accuracy:",round(accuracy*100,2),"%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    labels=sorted(y.unique()),
    zero_division=0
))

joblib.dump(model,"gesture_model.pkl")

print("Model saved as gesture_model.pkl")
print("Trained gestures:",model.classes_)
