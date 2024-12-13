
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
import joblib

class ArabicRecommender:
    def __init__(self):
        self.file_path = "datasets/arabic_news_labeled/arabic_news_labeled.csv"
        self.model = None
        self.tokenizer = None
        self.df_labeled_arabic_news = None
        self.df_mock_ar_news = None
        self.start()
        
    def init_model(self):
        model_name = "csebuetnlp/mT5_multilingual_XLSum"
        try:
            #self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            #self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            # Save the model and tokenizer to a local directory
            local_dir = "./models"
            #self.model.save_pretrained(local_dir)
            #self.tokenizer.save_pretrained(local_dir)
            # Save them locally using joblib
            self.tokenizer = joblib.load("./models/ar_tokenizer.joblib")
            self.model = joblib.load("./models/ar_model.joblib")
            print("[Arabic Recommender] Model initiated...")

        except Exception as e:
            print(f"[Arabic Recommender] Error initializing model or tokenizer: {e}")
            self.tokenizer = None
            self.model = None

    
    def load_arabic_news(self):
        self.df_labeled_arabic_news = pd.read_csv(self.file_path, encoding="utf-8")
        self.df_labeled_arabic_news['id'] = range(1, len(self.df_labeled_arabic_news) + 1)
        print("[Arabic Recommender] Arabic news uploaded...")
    
    def start(self):
        try:
            self.load_arabic_news()
            self.init_model()
            print("[Arabic Recommender] Initilized successfully...")
        except Exception as e:
            # Code to handle any other exception
            print(f"[Arabic Recommender] Unexpected error: {e}")
    
    def get_arabic_category(self):
        return self.df_labeled_arabic_news['predicted_category'].dropna().unique().tolist()
    
    def get_latest_arabic_news_by_category(self, category_id, max_return_news=4):
        """
        Fetch the latest Arabic news based on a given category ID.

        Args:
            category_id (str): The category ID to filter news.
            max_return_news (int): The maximum number of news articles to return.

        Returns:
            pd.DataFrame: A DataFrame containing the filtered news articles.
        """
        # Check if the news dataset is loaded
        if self.df_labeled_arabic_news is None:
            print("[Arabic Recommender] Arabic news data is not loaded.")
            return None

        # Filter news by category ID
        filtered_news = self.df_labeled_arabic_news[
            self.df_labeled_arabic_news["predicted_category"] == category_id
        ]

        # Sort by date (assuming a 'date_extracted' column exists)
        filtered_news = filtered_news.sort_values(
            by="date_extracted", ascending=False
        )

        # Limit the results to the specified maximum
        latest_news = filtered_news.head(max_return_news)

        return latest_news

    
    def get_arabic_news_by_id(self, news_id):
        """
        Fetch a specific Arabic news article by its unique ID.

        Args:
            news_id (int): The unique ID of the news article.

        Returns:
            pd.Series or None: The news article as a Pandas Series, or None if not found.
        """
        # Check if the news dataset is loaded
        if self.df_labeled_arabic_news is None:
            print("[Arabic Recommender] Arabic news data is not loaded.")
            return None

        # Filter the DataFrame to find the news by ID
        news_article = self.df_labeled_arabic_news[
            self.df_labeled_arabic_news["id"] == news_id
        ]

        # Check if any article is found
        if not news_article.empty:
            return news_article.iloc[0]  # Return the first matching article as a Series
        else:
            print(f"[Arabic Recommender] News with ID {news_id} not found.")
            return None

    
    def summarize_arabic_new(self, news_id):
        """
        Fetches an Arabic news article by its ID and generates a summary.

        Args:
            news_id (int): The unique ID of the news article to summarize.

        Returns:
            str or None: The summary of the news article, or None if not found.
        """
        # Fetch the news article by its ID
        news_article = self.get_arabic_news_by_id(news_id)

        if news_article is None:
            print(f"[Arabic Recommender] News with ID {news_id} not found or dataset not loaded.")
            return None

        # Extract the content of the news article
        content = news_article.get("content")
        
        if not content:
            print(f"[Arabic Recommender] No content available for news with ID {news_id}.")
            return None

        # Summarize the content using the summarization function
        try:
            summary = self.summarize_text(content)
            return summary
        except Exception as e:
            print(f"[Arabic Recommender] Error summarizing news: {e}")
            return None

    
    def summarize_text(self, text, max_length=100, min_length=30):
        if not text:
            print("[Arabic Recommender] Error: Provided text is None or empty.")
            return None

        if not self.tokenizer:
            print("[Arabic Recommender] Error: Tokenizer is not initialized.")
            return None

        try:
            inputs = self.tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                min_length=min_length,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return summary
        except Exception as e:
            print(f"[Arabic Recommender] Error in summarize_text: {e}")
            return None
