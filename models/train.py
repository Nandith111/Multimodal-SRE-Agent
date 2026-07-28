import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Mock data for training the initial gatekeeper model
# 1 = routine/known, 0 = novel/anomaly
training_data = [
    ("INFO [2026-07-19 08:00:00] User logged in successfully", 1),
    ("INFO [2026-07-19 08:01:00] Payment processed", 1),
    ("WARNING [2026-07-19 08:02:00] API rate limit approaching", 1),
    ("ERROR [2026-07-19 08:03:00] Invalid password attempt", 1),
    ("INFO [2026-07-19 08:04:00] Service started", 1),
    ("ERROR [2026-07-19 08:05:00] Cache miss", 1),
    ("ERROR [2026-07-19 08:57:22] - Thread-14: Unhandled pg8000.exceptions.DatabaseError: FATAL: remaining connection slots are reserved for non-replication superuser connections. Traceback", 0),
    ("CRITICAL [2026-07-19 09:00:00] Segmentation fault in core module", 0),
    ("ERROR [2026-07-19 09:05:00] OutOfMemoryError: Java heap space", 0)
]

def train_model():
    X, y = zip(*training_data)
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LogisticRegression(random_state=42, class_weight='balanced'))
    ])
    
    pipeline.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    with open('models/classifier.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
        
    print("Model trained and saved to models/classifier.pkl")

if __name__ == "__main__":
    train_model()
