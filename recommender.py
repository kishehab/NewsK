import pandas as pd
import joblib

class Recommender:
    def __init__(self):
        self.TFIDF_VECTORS_PATH = "models/dev_tfidf_vectors.joblib"
        self.load_models()
        print("recommender initilized...")
    
    def load_models(self):
        self.dev_tfidf = joblib.load(self.TFIDF_VECTORS_PATH)
        print("models loaded...")

rec =  Recommender()
    