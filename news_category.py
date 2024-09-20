import pandas as pd

class NewsCategory:
    def __init__(self, file_path):
        self.file_path = file_path
        self.column_names = ['ID', 'category', 'sub_category', 'title', 'abstract', 'url', 'title_entities', 'abstract_entities']
        self.df = None
        self.category_subcategory_mapping = None
        
    # Method to load the TSV file into a DataFrame
    def load_data(self):
        self.df = pd.read_csv(self.file_path, sep='\t', header=None, names=self.column_names)
    
    # Method to group by 'category' and aggregate 'sub_category' into lists
    def group_categories(self):
        if self.df is None:
            self.load_data()  # Load data if not already loaded
        
        self.category_subcategory_mapping = self.df.groupby('category')['sub_category'].apply(lambda x: list(x.unique())).reset_index()

    # Method to return the category and associated sub-categories
    def get_category_mapping(self):
        if self.category_subcategory_mapping is None:
            self.group_categories()  # Perform grouping if not already done
        
        return self.category_subcategory_mapping
    
    # New method to retrieve the most recent 10 news based on category and sub-categories
    def get_recent_news(self, selected_category, selected_subcategories):
        # Load the data if not already loaded
        if self.df is None:
            self.load_data()

        # Filter the DataFrame by the selected category and subcategories
        filtered_df = self.df[
            (self.df['category'] == selected_category) & 
            (self.df['sub_category'].isin(selected_subcategories))
        ]

        # Sort the filtered DataFrame by 'ID' (assuming higher ID means more recent) or use a date column if available
        sorted_df = filtered_df.sort_values(by='ID', ascending=False)

        # Select the top 10 most recent news articles
        recent_news = sorted_df.head(10)

        # Return relevant columns (e.g., 'title', 'abstract', 'url')
        return recent_news[['title', 'abstract', 'url']]
