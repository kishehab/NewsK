import pandas as pd
import joblib

class Recommender:
    def __init__(self):
        self.TFIDF_VECTORS_PATH = "models/dev_tfidf_vectors.joblib"
        self.load_models()
        print("recommender initilized successfully...")
    
    def load_models(self):
        self.dev_tfidf = joblib.load(self.TFIDF_VECTORS_PATH)
        print("models loaded...")

    def get_similar_article(id: int):
        return None
    