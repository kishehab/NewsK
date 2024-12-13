// Base URL for your Flask server
const BASE_URL = '';

// Fetch all categories
async function fetchCategories() {
    try {
        const response = await fetch(`${BASE_URL}/get_ar_category`);
        if (!response.ok) {
            throw new Error(`Error fetching categories: ${response.statusText}`);
        }
        const data = await response.json();
        console.log('Categories:', data);
        return data;
    } catch (error) {
        console.error(error);
    }
}

// Fetch news by ID
async function fetchNewsById(newsId) {
    try {
        const response = await fetch(`${BASE_URL}/get_ar_news_by_id?news_id=${newsId}`);
        if (!response.ok) {
            throw new Error(`Error fetching news by ID: ${response.statusText}`);
        }
        const data = await response.json();
        console.log(`News ID ${newsId}:`, data);
    } catch (error) {
        console.error(error);
    }
}

// Summarize news by ID
async function summarizeNewsById(newsId) {
    try {
        const response = await fetch(`${BASE_URL}/summarize_ar_news_by_id?news_id=${newsId}`);
        if (!response.ok) {
            throw new Error(`Error summarizing news by ID: ${response.statusText}`);
        }
        const data = await response.json();
        console.log(`Summary for News ID ${newsId}:`, data);
    } catch (error) {
        console.error(error);
    }
}

// Fetch news by category
async function fetchNewsByCategory(categoryId, maxReturnNews = 4) {
    try {
        const response = await fetch(`${BASE_URL}/get_ar_news_by_category?category_id=${categoryId}&max_return_news=${maxReturnNews}`);
        if (!response.ok) {
            throw new Error(`Error fetching news by category: ${response.statusText}`);
        }
        const data = await response.json();
        console.log(`News in category ${categoryId}:`, data);
    } catch (error) {
        console.error(error);
    }
}

// Define a global variable
let isArabicSwitched = false;

// Get the switch element
const switchElement = document.getElementById('arabicSwitch');

// Add an event listener to watch for changes
switchElement.addEventListener('change', (event) => {
  // Update the global variable based on the switch state
  isArabicSwitched = event.target.checked;
  if(isArabicSwitched){
    switchViewToArabic();
  }
});

document.getElementById("getSelectedButton").addEventListener("click", () => {
    if(isArabicSwitched){
        alert("fetch arabic ...");
    }

  });

function switchViewToArabic(){
    
}
setTimeout(() => {
// Example usage
fetchCategories(); // Fetch all categories
fetchNewsById(3); // Fetch news with ID 3
summarizeNewsById(3); // Summarize news with ID 3
fetchNewsByCategory('Politics', 3); // Fetch news in the "Politics" category, max 3 articles
}, 3000); // 30 seconds later

