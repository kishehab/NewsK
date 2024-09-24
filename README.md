
# NewsK: Personalized News Recommendation Platform 📰
![NEWSK](docs/NEWSK.png)

This web application leverages state-of-the-art AI and NLP to offer personalized news recommendations based on user preferences. By utilizing the power of Large Language Models (LLMs) and integrating both the MIND and SaudiNewsNet datasets, NewsK delivers an interactive experience that continuously evolves with new trends and user behavior.

## Features

- **Personalized Topic Selection**: Users can select their preferred news topics from a wide range of categories and subcategories.
- **Multi-Language Summarization**: The platform supports English and Arabic summaries using GPT-3, BART, and AraBERT.
- **Full Article View**: Users can access the full news article from the original source.
- **Related News Recommendations**: Get relevant news recommendations based on content similarity and time-relevance.
- **User Behavior Tracking**: Tracks user interactions to offer more personalized recommendations in the future.

## How It Works

1. **Data Ingestion and Preparation**:
   - Both the MIND and SaudiNewsNet datasets are ingested and stored in MongoDB for efficient querying. ETL processes are used to extract relevant fields like Title, Category, Date, and URL.

2. **Summarization**:
   - LLMs generate concise summaries in both English and Arabic. GPT-3 is used for English news, while AraBERT is utilized for Arabic content.

3. **User Topic Selection**:
   - Users choose topics from predefined categories. LLMs and topic modeling further classify news into subcategories.

4. **Content-Based Recommendations**:
   - Using embeddings from models like SentenceTransformers for English and AraBERT for Arabic, the platform calculates cosine similarity to recommend articles.

5. **User Behavior Tracking and Recommendations**:
   - The platform keeps track of the user's interaction to improve future recommendations through a feedback loop.

## Installation

Follow these steps to run this application locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/NewsK.git
   ```

2. **Navigate to the Repository Directory**:
   ```bash
   cd NewsK
   ```

3. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py  
   ```

## Datasets

- **MIND Dataset**: Provides user behaviors and news metadata (behaviors.tsv and news.tsv files).
- **SaudiNewsNet Dataset**: Contains 31,030 Arabic news articles organized by date.

## Technology Stack

- **Backend**: Flask
- **Frontend**: Vue.js
- **Database**: MongoDB
- **LLMs for Summarization**: GPT-3, AraBERT, BART, T5
- **Deployment**: Docker

## Future Enhancements

- **Real-Time News Integration**: Add support for real-time news feeds from APIs and RSS to continuously update the dataset.
- **Multi-Language Expansion**: Extend support to other languages to cater to a broader audience.
- **User Feedback Loop**: Incorporate a system for user feedback to improve recommendation quality.


---
