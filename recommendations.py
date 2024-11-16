import pandas as pd
import joblib
from collections import defaultdict
import numpy as np

# Define file paths for saved models and data
TFIDF_VECTORS_PATH = "dev_tfidf_vectors.joblib"
LLM_EMBEDDINGS_PATH = "dev_llm_embeddings.joblib"
COSINE_SIM_TFIDF_PATH = "cosine_sim_tfidf.joblib"
COSINE_SIM_LLM_PATH = "cosine_sim_llm.joblib"
DEV_NEWS_PATH = "dev_news.csv"
DEV_BEHAVIORS_PATH = "dev_behaviors.csv"

# Function to Load Precomputed Data
def load_precomputed_data():
    dev_tfidf = joblib.load(TFIDF_VECTORS_PATH)
    dev_embeddings = joblib.load(LLM_EMBEDDINGS_PATH)
    cosine_sim_tfidf = joblib.load(COSINE_SIM_TFIDF_PATH)
    cosine_sim_llm = joblib.load(COSINE_SIM_LLM_PATH)
    dev_news = pd.read_csv(DEV_NEWS_PATH)
    dev_behaviors = pd.read_csv(DEV_BEHAVIORS_PATH)
    return dev_tfidf, dev_embeddings, cosine_sim_tfidf, cosine_sim_llm, dev_news, dev_behaviors

# Load precomputed data
dev_tfidf, dev_embeddings, cosine_sim_tfidf, cosine_sim_llm, dev_news, dev_behaviors = load_precomputed_data()

# Function to Get Similar Articles
def get_similar_articles(article_id: str, news_df: pd.DataFrame, cosine_sim: np.ndarray, num_recommendations: int = 5) -> pd.DataFrame:
    """Get similar articles based on cosine similarity."""
    idx = news_df[news_df['itemId'] == article_id].index[0]
    sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)[1:num_recommendations+1]
    return pd.DataFrame({
        'itemId': [news_df.iloc[i]['itemId'] for i, _ in sim_scores],
        'title': [news_df.iloc[i]['title'] for i, _ in sim_scores],
        'abstract': [news_df.iloc[i]['abstract'] for i, _ in sim_scores],
        'category': [news_df.iloc[i]['category'] for i, _ in sim_scores],
        'subcategory': [news_df.iloc[i]['subcategory'] for i, _ in sim_scores],
        'similarity_score': [score for _, score in sim_scores]
    })

# Function to Get User Recommendations
def get_user_recommendations(user_id: str, behaviors_df: pd.DataFrame, news_df: pd.DataFrame, cosine_sim: np.ndarray, num_recommendations: int = 5) -> pd.DataFrame:
    """Get recommendations for a user based on their click history."""
    user_history = behaviors_df[behaviors_df['userId'] == user_id]['click_history'].iloc[0].split()
    user_indices = [news_df[news_df['itemId'] == item_id].index[0] for item_id in user_history if item_id in news_df['itemId'].values]

    if not user_indices:
        return pd.DataFrame(columns=['itemId', 'title', 'abstract', 'similarity_score'])

    sim_scores = defaultdict(float)
    for idx in user_indices:
        similar_articles = list(enumerate(cosine_sim[idx]))
        for i, score in similar_articles:
            sim_scores[i] += score

    sorted_scores = sorted(sim_scores.items(), key=lambda x: x[1], reverse=True)
    recommended_indices = [i for i, score in sorted_scores if news_df.iloc[i]['itemId'] not in user_history][:num_recommendations]

    recommendations = pd.DataFrame({
        'itemId': [news_df.iloc[i]['itemId'] for i in recommended_indices],
        'title': [news_df.iloc[i]['title'] for i in recommended_indices],
        'abstract': [news_df.iloc[i]['abstract'] for i in recommended_indices],
        'category': [news_df.iloc[i]['category'] for i in recommended_indices],
        'subcategory': [news_df.iloc[i]['subcategory'] for i in recommended_indices],
        'similarity_score': [sim_scores[i] for i in recommended_indices]
    })

    return recommendations

# Example usage: Recommend similar articles
article_id = dev_news['itemId'].iloc[0]
similar_articles = get_similar_articles(article_id, dev_news, cosine_sim_llm)
print(similar_articles)

# Example usage: Recommend articles for a user
user_id = dev_behaviors['userId'].iloc[0]
user_recommendations = get_user_recommendations(user_id, dev_behaviors, dev_news, cosine_sim_llm)
print(user_recommendations)
