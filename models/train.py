import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def train_and_evaluate():
    data_path = os.path.join(os.path.dirname(__file__), 'synthetic_logs.csv')
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run generate_logs.py first.")
        return

    # Load the data
    df = pd.read_csv(data_path)
    X = df['message']
    y = df['label']

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define models to evaluate
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(random_state=42, class_weight='balanced', n_estimators=100),
        'Linear SVC': LinearSVC(random_state=42, class_weight='balanced')
    }

    best_model_name = None
    best_f1_score = -1.0
    best_pipeline = None

    print("Evaluating models...\n" + "-"*30)

    for name, model in models.items():
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english')),
            ('clf', model)
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Predict on test set
        y_pred = pipeline.predict(X_test)
        
        # Calculate metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='binary', zero_division=0)
        rec = recall_score(y_test, y_pred, average='binary', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
        
        print(f"Model: {name}")
        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1-Score:  {f1:.4f}\n")
        
        # Check if this is the best model based on F1-Score
        if f1 > best_f1_score:
            best_f1_score = f1
            best_model_name = name
            best_pipeline = pipeline

    print("-" * 30)
    print(f"Best Model: {best_model_name} (F1-Score: {best_f1_score:.4f})")
    
    # Save the best model
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    model_save_path = os.path.join(os.path.dirname(__file__), 'classifier.pkl')
    
    with open(model_save_path, 'wb') as f:
        pickle.dump(best_pipeline, f)
        
    print(f"Best model trained and saved to {model_save_path}")

if __name__ == "__main__":
    train_and_evaluate()
