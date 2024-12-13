from flask import Flask, render_template_string, request, jsonify
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import torch
import json
from langdetect import detect, LangDetectException

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NewsK AI Advisor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --background-color: #f8fafc;
            --card-background: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
        }

        body {
            background-color: var(--background-color);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }

        .nav-bar {
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .nav-bar h1 {
            color: white;
            margin: 0;
            font-size: 1.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .card {
            background: var(--card-background);
            border-radius: 1rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.1);
        }

        .chat-container {
            height: 65vh;
            overflow-y: auto;
            padding: 1.5rem;
            margin-bottom: 1rem;
            scroll-behavior: smooth;
        }

        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 1rem;
            max-width: 85%;
            position: relative;
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .ai-message {
            background-color: #f1f5f9;
            color: var(--text-primary);
            margin-right: auto;
            border-bottom-left-radius: 0.25rem;
        }

        .human-message {
            background-color: var(--primary-color);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 0.25rem;
        }

        .insight-card {
            margin-bottom: 1.5rem;
        }

        .insight-card h5 {
            color: var(--text-primary);
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .insight-item {
            padding: 0.75rem;
            border-radius: 0.5rem;
            background-color: #f8fafc;
            margin-bottom: 0.75rem;
            transition: background-color 0.2s;
        }

        .insight-item:hover {
            background-color: #f1f5f9;
        }

        .insight-item strong {
            color: var(--primary-color);
            font-weight: 600;
        }

        .input-group {
            background: white;
            border-radius: 0.75rem;
            padding: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .form-control {
            border: none;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            background: transparent;
            color: var(--text-primary);
        }

        .form-control:focus {
            box-shadow: none;
            outline: none;
        }

        .btn-primary {
            background-color: var(--primary-color);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 500;
            transition: background-color 0.2s;
        }

        .btn-primary:hover {
            background-color: var(--secondary-color);
        }

        .spinner-border {
            width: 1.5rem;
            height: 1.5rem;
            border-width: 0.2rem;
            display: none;
        }

        .spinner-border.active {
            display: inline-block;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f5f9;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }

        /* Animations */
        .fade-in {
            animation: fadeIn 0.3s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .chat-container {
                height: 50vh;
            }
            
            .message {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <nav class="nav-bar">
        <div class="container">
            <h1><i class="fas fa-robot"></i> NewsK AI Advisor</h1>
        </div>
    </nav>

    <div class="container py-4">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card insight-card mb-4 fade-in" id="analysisCard" style="display: none;">
                    <div class="card-body">
                        <h5><i class="fas fa-chart-bar me-2"></i>Article Insights</h5>
                        <div class="insight-item">
                            <strong><i class="fas fa-file-alt me-2"></i>Summary:</strong>
                            <p id="articleSummary" class="mb-0 mt-2"></p>
                        </div>
                        <div class="insight-item">
                            <strong><i class="fas fa-folder me-2"></i>Category:</strong>
                            <p id="articleCategory" class="mb-0 mt-2"></p>
                        </div>
                        <div class="insight-item">
                            <strong><i class="fas fa-heart me-2"></i>Sentiment:</strong>
                            <p id="articleSentiment" class="mb-0 mt-2"></p>
                        </div>
                        <div class="insight-item">
                            <strong><i class="fas fa-tags me-2"></i>Keywords:</strong>
                            <p id="articleKeywords" class="mb-0 mt-2"></p>
                        </div>
                    </div>
                </div>
                
                <div class="card insight-card fade-in">
                    <div class="card-body">
                        <h5><i class="fas fa-cog me-2"></i>Settings</h5>
                        <div class="mb-3">
                            <input type="text" id="urlInput" class="form-control" 
                                   placeholder="Enter article URL">
                        </div>
                        <button onclick="processArticle()" class="btn btn-primary w-100 mb-3">
                            <i class="fas fa-sync-alt me-2"></i>Process Article
                        </button>
                        <div class="text-center">
                            <div id="loadingSpinner" class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                        <small class="text-muted">
                            <i class="fas fa-info-circle me-1"></i>
                            Provide a URL to analyze an online article
                        </small>
                    </div>
                </div>
            </div>
            
            <div class="col-md-8">
                <div class="card h-100">
                    <div class="card-body p-0 d-flex flex-column">
                        <div id="chatContainer" class="chat-container">
                            <div class="message ai-message fade-in">
                                <i class="fas fa-robot me-2"></i>Hello! I'm your NewsK AI Advisor. 
                                How can I help you analyze articles today?
                            </div>
                        </div>
                        
                        <div class="p-3">
                            <div class="input-group">
                                <input type="text" id="userInput" class="form-control" 
                                       placeholder="Ask me anything about the article...">
                                <button class="btn btn-primary" onclick="sendMessage()">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        let vectorStoreReady = false;
        let chatHistory = [];

        function showSpinner() {
            document.getElementById('loadingSpinner').classList.add('active');
        }

        function hideSpinner() {
            document.getElementById('loadingSpinner').classList.remove('active');
        }

        function processArticle() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                showToast('Please enter a valid URL');
                return;
            }

            showSpinner();
            addMessage('Processing article... This may take a moment. ⏳', 'ai');

            $.ajax({
                url: '/process_article',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ url: url }),
                success: function(response) {
                    hideSpinner();
                    if (response.success) {
                        vectorStoreReady = true;
                        addMessage('Article processed successfully! 🎉 You can now ask questions about it.', 'ai');
                        
                        const analysisCard = document.getElementById('analysisCard');
                        analysisCard.style.display = 'block';
                        analysisCard.classList.add('fade-in');
                        
                        document.getElementById('articleSummary').textContent = response.analysis.summary || '';
                        document.getElementById('articleCategory').textContent = response.analysis.category || '';
                        document.getElementById('articleSentiment').textContent = response.analysis.sentiment || '';
                        document.getElementById('articleKeywords').textContent = response.analysis.keywords || '';
                    } else {
                        addMessage('Failed to process article. Please check the URL and try again. ❌', 'ai');
                    }
                },
                error: function() {
                    hideSpinner();
                    addMessage('Error processing article. Please try again. ❌', 'ai');
                }
            });
        }

        function sendMessage() {
            if (!vectorStoreReady) {
                showToast('Please process an article first');
                return;
            }

            const userInput = document.getElementById('userInput');
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, 'human');
            userInput.value = '';

            $.ajax({
                url: '/chat',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 
                    message: message,
                    chat_history: chatHistory
                }),
                beforeSend: function() {
                    showSpinner();
                },
                success: function(response) {
                    hideSpinner();
                    addMessage(response.response, 'ai');
                },
                error: function() {
                    hideSpinner();
                    addMessage('Error generating response. Please try again. ❌', 'ai');
                }
            });
        }

        function addMessage(message, sender) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${sender}-message`, 'fade-in');
            
            if (sender === 'ai') {
                messageDiv.innerHTML = `<i class="fas fa-robot me-2"></i>${message}`;
            } else {
                messageDiv.innerHTML = `<i class="fas fa-user me-2"></i>${message}`;
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            chatHistory.push({"role": sender, "content": message});
        }

        function showToast(message) {
            // You can implement a custom toast notification here
            alert(message);
        }

        document.getElementById('userInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

# Configure device for Apple Silicon if available
device = "mps" if torch.backends.mps.is_available() else "cpu"

def initialize_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device},
        encode_kwargs={'device': device, 'batch_size': 32}
    )

def get_vectorstore_from_url(url):
    try:
        loader = WebBaseLoader(url)
        document = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len
        )
        document_chunks = text_splitter.split_documents(document)
        embeddings = initialize_embeddings()
        
        vector_store = FAISS.from_documents(
            document_chunks, 
            embeddings
        )
        return vector_store, document
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None, None

def get_llm():
    try:
        return Ollama(
            model="llama3.3:latest ",
            temperature=0.7,
            num_ctx=4096,
            num_gpu=1,
            num_thread=4
        )
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return None

def get_context_retriever_chain(vector_store, lang):
    llm = get_llm()
    if not llm:
        return None
        
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )
    
    # Add language instructions in the prompt
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", f"Given the article we processed, provide information and insights based on its content. Respond in {lang}.")
    ])
    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain

def get_conversational_rag_chain(retriever_chain, lang):
    llm = get_llm()
    if not llm or not retriever_chain:
        return None
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful AI assistant analyzing articles. Provide relevant, fact-based answers derived from the article content. Respond in {lang}.\n\n{{context}}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def analyze_article_content(doc_text, lang):
    llm = get_llm()
    if llm is None:
        return {"summary": "", "category": "", "sentiment": "", "keywords": ""}

    # Updated prompt to ensure the response is in the detected language
    prompt = (
        f"You are a helpful AI news assistant analyzing the content of an article. Respond in {lang}.\n"
        "Return a JSON object with the following fields:\n\n"
        "summary: A concise summary of the article.\n"
        "category: The main category or topic of the article (Politics, Finance, Technology, Religion, Culture, Medical, etc.).\n"
        "sentiment: A single word describing the overall sentiment (positive, negative, or neutral).\n"
        "keywords: A list of the most important words or phrases capturing the article's main ideas.\n\n"
        "Your response must be strictly valid JSON with no additional commentary."
    )

    response = llm.invoke([HumanMessage(content=prompt + "\n\n" + doc_text)])
    text = response.strip()

    # Attempt JSON parsing with fallback
    try:
        data = json.loads(text)
    except:
        import re
        json_pattern = re.compile(r'\{(?:[^{}]|(?R))*\}', re.DOTALL)
        match = json_pattern.search(text)
        if match:
            try:
                data = json.loads(match.group(0))
            except:
                data = {}
        else:
            data = {}

    # Ensure all keys exist
    for key in ["summary", "category", "sentiment", "keywords"]:
        if key not in data:
            data[key] = ""

    # If sentiment is an object, flatten it to string
    if isinstance(data["sentiment"], dict):
        sentiment_value = data["sentiment"].get("value", "")
        data["sentiment"] = sentiment_value if sentiment_value else "neutral"

    # If keywords is a list, convert to comma-separated string
    if isinstance(data["keywords"], list):
        data["keywords"] = ", ".join(data["keywords"])

    return data

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process_article', methods=['POST'])
def process_article():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    vector_store, document = get_vectorstore_from_url(url)
    if vector_store:
        app.vector_store = vector_store
        
        full_text = document[0].page_content if document else ""
        
        # Detect language code
        try:
            lang_code = detect(full_text)
        except LangDetectException:
            lang_code = "ar"  # Default fallback

        # Map language code to full language name
        lang_map = {
            "ar": "Arabic",
            "en": "English",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "zh-cn": "Chinese (Simplified)",
            "zh-tw": "Chinese (Traditional)",
            "ja": "Japanese",
            "ko": "Korean",
            "nl": "Dutch",
            "sv": "Swedish",
            "no": "Norwegian",
            "fi": "Finnish",
            "da": "Danish",
            "pl": "Polish",
            "cs": "Czech",
            "tr": "Turkish",
            "el": "Greek",
            "he": "Hebrew",
            "id": "Indonesian",
            "hi": "Hindi",
            "th": "Thai",
        }

        lang = lang_map.get(lang_code, "Unknown")

        # Store the language globally for the conversation
        app.language = lang
        
        analysis = analyze_article_content(full_text, lang)
        
        return jsonify({'success': True, 'analysis': analysis})
    else:
        return jsonify({'success': False, 'error': 'Failed to process article'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    chat_history = data.get('chat_history', [])
    
    if not hasattr(app, 'vector_store'):
        return jsonify({'success': False, 'error': 'No article processed'})
    
    lang = getattr(app, 'language', 'en')
    
    try:
        # Convert chat history to LangChain format
        formatted_history = []
        for msg in chat_history:
            if msg['role'] == 'human':
                formatted_history.append(HumanMessage(content=msg['content']))
            else:
                formatted_history.append(AIMessage(content=msg['content']))
        
        retriever_chain = get_context_retriever_chain(app.vector_store, lang)
        if not retriever_chain:
            return jsonify({'success': False, 'response': 'Error processing request'})
            
        conversational_rag_chain = get_conversational_rag_chain(retriever_chain, lang)
        if not conversational_rag_chain:
            return jsonify({'success': False, 'response': 'Error processing request'})
            
        response = conversational_rag_chain.invoke({
            "chat_history": formatted_history,
            "input": message,
        })
        
        return jsonify({'success': True, 'response': response['answer']})
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return jsonify({'success': False, 'response': 'Error generating response'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)