from flask import Flask, request, jsonify, render_template
from news_category import NewsCategory
import json
import sys
sys.path.append("c:\\python310\\lib\\site-packages")
from tinydb import TinyDB, Query


app = Flask(__name__)

# Initialize TinyDB (stores data in a JSON file)
db = TinyDB('db.json')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    city = data.get('city')
    
    # Insert user into TinyDB
    db.insert({'name': name, 'age': age, 'city': city})
    
    return jsonify({'message': 'User added successfully!'})

@app.route('/list_users', methods=['GET'])
def list_users():
    # Retrieve all users
    users = db.all()
    return jsonify(users)

@app.route('/get_category', methods=['GET'])
def get_category():
    # Example usage:
    file_path = 'datasets/MINDsmall_train/news.tsv'
    news_category = NewsCategory(file_path)
    category_mapping = news_category.get_category_mapping()
    # Convert DataFrame to a dictionary (or you can use 'records' for a list of dictionaries)
    df_dict = category_mapping.to_dict(orient='records')

    # Now df_dict is JSON serializable
    json_data = json.dumps(df_dict, indent=4)
    # Display the category mapping
    return jsonify(df_dict)

# NEW ENDPOINT: Receive selection and return the 10 most recent news items
@app.route('/get_recent_news', methods=['POST'])
def get_recent_news():
    # Example usage of NewsCategory class
    file_path = 'datasets/MINDsmall_train/news.tsv'
    news_category = NewsCategory(file_path)

    # Get data from the request (JSON body)
    data = request.json

    # Initialize a list to collect all recent news for each category
    all_recent_news = []

    # Iterate over the list of categories and their selected subcategories
    for selection in data:
        selected_category = selection.get('category')
        selected_subcategories = selection.get('selectedSubcategories')

        # Validate input for each category
        if not selected_category or not selected_subcategories:
            continue

        # Retrieve recent news for the current category and subcategories
        recent_news = news_category.get_recent_news(selected_category, selected_subcategories)

        # Handle NaN values by replacing them with None (null in JSON)
        recent_news = recent_news.fillna(value='')

        # Convert the result to a JSON-serializable format
        news_json = recent_news.to_dict(orient='records')

        # Append the result to the all_recent_news list
        all_recent_news.extend(news_json)

    # Return all the collected recent news as JSON
    return jsonify(all_recent_news)

if __name__ == '__main__':
    app.run(debug=True)

