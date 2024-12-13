import pandas as pd
import joblib
from collections import defaultdict

class EnglishRecommender:
    def __init__(self):
        # path to news dataset
        self.DEV_NEWS_PATH = "datasets/MINDsmall_dev/dev_news.tsv"
        self.DEV_BEHAVIORS_PATH = "datasets/behaviors/dev_behaviors.tsv"
        # columns name of the news dataset
        self.column_names = ['ID', 'category', 'sub_category', 'title', 'abstract', 'url', 'title_entities', 'abstract_entities']
        self.behaviors_columns = ["impressionId", "userId", "timestamp", "click_history", "impressions"]
        # paths to models
        self.TFIDF_VECTORS_PATH = "models/dev_tfidf_vectors.joblib"
        self.LLM_EMBEDDINGS_PATH = "models/dev_llm_embeddings.joblib"
        self.COSINE_SIM_TFIDF_PATH = "models/cosine_sim_tfidf.joblib"
        self.COSINE_SIM_LLM_PATH = "models/cosine_sim_llm.joblib"

        # load model and article data
        self.load_models()
        self.load_articles()
        print("[English Recommender] initilized successfully...")
    
    def load_articles(self):
        self.news_df = pd.read_csv(self.DEV_NEWS_PATH, sep="\t",names=self.column_names)
        print("[English Recommender] articles loaded successfully...")
        self.behaviors_df = pd.read_csv(self.DEV_BEHAVIORS_PATH, sep="\t",names=self.behaviors_columns)
        print("[English Recommender] articles loaded successfully...")
    
    def load_models(self):
        self.dev_tfidf = joblib.load(self.TFIDF_VECTORS_PATH)
        self.dev_embeddings = joblib.load(self.LLM_EMBEDDINGS_PATH)
        #self.cosine_sim_tfidf = joblib.load(self.COSINE_SIM_TFIDF_PATH)
        self.cosine_sim_llm = joblib.load(self.COSINE_SIM_LLM_PATH)
        print("[English Recommender] models loaded successfully...")

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
    
    def get_user_recommendations(self, user_id: str, num_recommendations: int = 5):
        """Get recommendations for a user based on their click history."""

        # Find articles clicked by the user
        user_history = self.behaviors_df[self.behaviors_df['userId'] == user_id]['click_history'].iloc[0].split()  # List of clicked article IDs
        user_indices = [self.news_df[self.news_df['ID'] == item_id].index[0] for item_id in user_history if item_id in self.news_df['ID'].values]

        # If user has no history, return most popular articles or random recommendations
        if not user_indices:
            return pd.DataFrame(columns=['ID', 'title', 'abstract', 'similarity_score'])

        # Calculate similarity scores for each article in user history
        sim_scores = defaultdict(float)
        for idx in user_indices:
            similar_articles = list(enumerate(self.cosine_sim_llm[idx]))
            for i, score in similar_articles:
                sim_scores[i] += score  # Accumulate similarity scores

        # Sort and select top recommendations not in user's click history
        sorted_scores = sorted(sim_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_indices = [i for i, score in sorted_scores if self.news_df.iloc[i]['ID'] not in user_history][:num_recommendations]

        # Create a DataFrame for the recommended articles
        #self.column_names = ['ID', 'category', 'sub_category', 'title', 'abstract', 'url', 'title_entities', 'abstract_entities']
        recommendations = pd.DataFrame({
            'ID': [self.news_df.iloc[i]['ID'] for i in recommended_indices],
            'title': [self.news_df.iloc[i]['title'] for i in recommended_indices],
            'abstract': [self.news_df.iloc[i]['abstract'] for i in recommended_indices],
            'category': [self.news_df.iloc[i]['category'] for i in recommended_indices],
            'sub_category': [self.news_df.iloc[i]['sub_category'] for i in recommended_indices],
            'similarity_score': [sim_scores[i] for i in recommended_indices]
        })

        return recommendations
    
    def get_insights(self):
       
        behaviors_data = self.behaviors_df
        news_data = self.news_df

        # Behaviors Insights
        total_users = int(behaviors_data['userId'].nunique())  # Convert to int
        total_impressions = int(len(behaviors_data))  # Convert to int
        most_active_users = behaviors_data['userId'].value_counts().head(5).to_dict()

        # Parse impressions to calculate CTR
        impressions_data = behaviors_data['impressions'].str.split(' ').explode()
        impressions_data = impressions_data.str.split('-', expand=True)
        impressions_data.columns = ['news_id', 'clicked']
        impressions_data['clicked'] = impressions_data['clicked'].astype(int)

        total_articles = int(impressions_data['news_id'].nunique())
        clicked_articles = int(impressions_data[impressions_data['clicked'] == 1].count()['news_id'])
        ctr = float(clicked_articles / len(impressions_data))  # Convert to float

        # Average and maximum click history length
        click_history_lengths = behaviors_data['click_history'].dropna().str.split(' ').apply(len)
        avg_click_history = float(click_history_lengths.mean())
        max_click_history = int(click_history_lengths.max())

        # News Insights
        total_news = int(len(news_data))
        category_distribution = news_data['category'].value_counts().to_dict()
        subcategory_distribution = news_data['sub_category'].value_counts().to_dict()

        # Content Length Metrics
        title_lengths = news_data['title'].str.len()
        abstract_lengths = news_data['abstract'].str.len()

        avg_title_length = float(title_lengths.mean())
        max_title_length = int(title_lengths.max())
        min_title_length = int(title_lengths.min())

        avg_abstract_length = float(abstract_lengths.mean())
        max_abstract_length = int(abstract_lengths.max())
        min_abstract_length = int(abstract_lengths.min())

        # Compile insights
        insights = {
            "behaviors_insights": {
                "total_users": total_users,
                "total_impressions": total_impressions,
                "most_active_users": most_active_users,
                "click_through_rate": ctr,
                "avg_click_history_length": avg_click_history,
                "max_click_history_length": max_click_history,
            },
            "news_insights": {
                "total_news_articles": total_news,
                "category_distribution": category_distribution,
                "subcategory_distribution": subcategory_distribution,
                "avg_title_length": avg_title_length,
                "max_title_length": max_title_length,
                "min_title_length": min_title_length,
                "avg_abstract_length": avg_abstract_length,
                "max_abstract_length": max_abstract_length,
                "min_abstract_length": min_abstract_length,
            },
            "combined_insights": {
                "most_clicked_categories": impressions_data.merge(news_data, left_on='news_id', right_on='ID')['category'].value_counts().head(5).to_dict(),
                "ctr_by_category": impressions_data.merge(news_data, left_on='news_id', right_on='ID').groupby('category').apply(lambda x: float((x['clicked'] == 1).sum() / len(x))).to_dict(),
            }
        }

        return insights