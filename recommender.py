import pandas as pd
import joblib

class Recommender:
    def __init__(self):
        # path to news dataset
        self.DEV_NEWS_PATH = "datasets/MINDsmall_dev/dev_news.tsv"
        # columns name of the news dataset
        self.column_names = ['ID', 'category', 'sub_category', 'title', 'abstract', 'url', 'title_entities', 'abstract_entities']
        # paths to models
        self.TFIDF_VECTORS_PATH = "models/dev_tfidf_vectors.joblib"
        self.LLM_EMBEDDINGS_PATH = "models/dev_llm_embeddings.joblib"
        self.COSINE_SIM_TFIDF_PATH = "models/cosine_sim_tfidf.joblib"
        self.COSINE_SIM_LLM_PATH = "models/cosine_sim_llm.joblib"

        # load model and article data
        self.load_models()
        self.load_articles()
        print("[Recommender] initilized successfully...")
    
    def load_articles(self):
        self.news_df = pd.read_csv(self.DEV_NEWS_PATH, sep="\t",names=self.column_names)
        print("[Recommender] articles loaded successfully...")
    
    def load_models(self):
        self.dev_tfidf = joblib.load(self.TFIDF_VECTORS_PATH)
        self.dev_embeddings = joblib.load(self.LLM_EMBEDDINGS_PATH)
        #self.cosine_sim_tfidf = joblib.load(self.COSINE_SIM_TFIDF_PATH)
        self.cosine_sim_llm = joblib.load(self.COSINE_SIM_LLM_PATH)
        print("[Recommender] models loaded successfully...")

    def get_similar_articles(self, article_id: str, num_recommendations: int = 3):
        """
        Retrieve similar articles for a given article ID.

        Parameters:
        - article_id (str): The ID of the article for which to find similar articles.
        - num_recommendations (int): Number of similar articles to return.

        Returns:
        - dict: A dictionary of similar articles with their details.
        """
        # Ensure the article_id is mapped to a valid index
        if article_id not in self.news_df['ID'].values:
            raise ValueError(f"Article ID '{article_id}' not found in the dataset.")

        # Find the index of the article_id
        article_index = self.news_df[self.news_df['ID'] == article_id].index[0]

        # Compute similarity scores for the given article
        sim_scores = list(enumerate(self.cosine_sim_llm[article_index]))

        # Sort by similarity score, excluding the article itself
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:num_recommendations+1]

        # Fetch article details from the dataframe
        similar_articles = [
            {
                'ID': self.news_df.iloc[i]['ID'],
                'title': self.news_df.iloc[i]['title'],
                'abstract': self.news_df.iloc[i]['abstract'],
                'url': self.news_df.iloc[i]['url'],
                'category': self.news_df.iloc[i]['category'],
                'similarity_score': float(score)  # Convert numpy.float32 to native float
            }
            for i, score in sim_scores
        ]

        return similar_articles
