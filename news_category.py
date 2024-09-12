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
