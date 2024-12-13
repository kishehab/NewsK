console.log("Main Arabic JS is running...");
// Import a function from cookies.js
import { getOrCreateUniqueNumber } from "./cookies.js";
import { CategoryManager } from "./CategoryManager.js"; // Import CategoryManager
window.onload = function () {
  const BASE_URL = "";
  console.log("Page has fully loaded!");
  // initiate news modal
  const newsModal = new bootstrap.Modal("#newsModal");
  var selectedCategory = "";
  var globalNewsData = [];
  const maxLengthTtile = 100;
  const maxLengthAbstract = 150;
  // Function to list all users
  async function listUsers() {
    const response = await fetch("/list_users", {
      method: "GET",
    });
    const users = await response.json();
    // Clear the current list
    const userList = document.getElementById("userList");
    userList.innerHTML = "";
    // Populate the user list
    users.forEach((user) => {
      const li = document.createElement("li");
      li.textContent = `Name: ${user.name}, Age: ${user.age}, City: ${user.city}`;
      userList.appendChild(li);
    });
  }
  // main.js
  const categoryManager = new CategoryManager();
  // Fetch the categories and sub-categories from the server
  async function get_category() {
    //categorySpinner
    const categorySpinner = document.getElementById("categorySpinner");
    try {
      // Show the spinner
      categorySpinner.classList.remove("d-none");
      const response = await fetch("/get_category", {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching category:", error);
      alert("Failed to fetch categories");
    } finally {
      // Hide spinner
      categorySpinner.classList.add("d-none");
    }
  }
  // Function to display categories
  function displayCategories() {
    const categoryContainer = document.getElementById("category-container");
    categoryContainer.innerHTML = ""; // Clear the container
    categoryManager.categories.forEach((category) => {
      const categoryBadge = document.createElement("span");
      categoryBadge.className = "badge bg-primary m-2 px-4 category-badge"; // Bootstrap badge
      categoryBadge.textContent = category.name;
      // Create a span for the selected subcategory counter
      const counterBadge = document.createElement("span");
      counterBadge.className = "bg-light text-dark m-2 px-1 counter-badge";
      counterBadge.textContent = `${category.getSelectedSubcategoryCount()}`; // Show the initial count as 0
      // Add event listener to handle category click
      categoryBadge.addEventListener("click", () => {
        categoryManager.setSelectedCategory(category.name); // Set selected category
        displaySubcategories(category, counterBadge); // Pass the counterBadge to update the count later
      });
      // Append the category badge and counter to the container
      categoryBadge.appendChild(counterBadge);
      // hide if 0
      if (counterBadge.textContent == 0) {
        counterBadge.style.display = "none";
      }
      categoryContainer.appendChild(categoryBadge);
    });
  }
  // Function to display subcategories for the selected category
  function displaySubcategories(category, counterBadge) {
    const subcategoryContainer = document.getElementById(
      "subcategory-container"
    );
    subcategoryContainer.innerHTML = ""; // Clear the container
    subcategoryContainer.classList.remove("d-none");
    category.subcategories.forEach((subcategory) => {
      const subCategoryBadge = document.createElement("span");
      subCategoryBadge.className = "badge bg-secondary m-2 subcategory-badge"; // Bootstrap badge
      subCategoryBadge.textContent = subcategory;
      // Check if the subcategory is already selected and add a selected class if true
      if (category.selectedSubcategories.includes(subcategory)) {
        subCategoryBadge.classList.add("selected");
      }
      // Add click event listener to toggle subcategory selection
      subCategoryBadge.addEventListener("click", function () {
        categoryManager.selectedCategory.toggleSubcategory(subcategory); // Toggle selection
        // Toggle visual indication of selection
        this.classList.toggle("selected");
        // Update the subcategory counter
        counterBadge.textContent = `${category.getSelectedSubcategoryCount()}`;
        // unhide if selected
        if (counterBadge.textContent > 0) {
          counterBadge.style.display = "";
        }
      });
      // Append the subcategory badge to the container
      subcategoryContainer.appendChild(subCategoryBadge);
    });
  }
  // NEW FUNCTION: Fetch and log all selected categories and subcategories
  function getSelectedCategoriesAndSubcategories() {
    const selectedData = categoryManager.getAllSelectedCategories();
    console.log("All selected categories and subcategories:", selectedData);
    return selectedData;
  }
  // Add a button to fetch all selected categories and subcategories
  document.getElementById("getSelectedButton").addEventListener("click", () => {
    const button = document.getElementById("getSelectedButton");
    const spinner = document.getElementById("buttonSpinner");
    const newsContainer = document.getElementById("newsContainer");
    try {
      // Show the spinner
      spinner.classList.remove("d-none");
      button.setAttribute("disabled", true);
      fetchNewsByCategory(selectedCategory).then(function (arabicNews) {
        console.log(arabicNews);
        globalNewsData = arabicNews;
        displayNews(arabicNews);
        const offset = 100; // Adjust this value as needed (e.g., 100px)
        const newsContainerPosition =
          newsContainer.getBoundingClientRect().top +
          window.pageYOffset -
          offset;
        // Scroll to the calculated position with a smooth effect
        window.scrollTo({ top: newsContainerPosition, behavior: "smooth" });
      });
    } catch (error) {
      console.error("Failed to fetch recent news:", error);
    } finally {
      // Hide the spinner and re-enable the button
      spinner.classList.add("d-none");
      button.removeAttribute("disabled");
    }
  });
  // Fetch categories and initialize the page
  fetchCategories().then(function (response) {
    if (response) {
      const categoryContainer = document.getElementById("category-container");
      categoryContainer.innerHTML = ""; // Clear the container
      response.forEach((category) => {
        const categoryBadge = document.createElement("span");
        categoryBadge.className = "badge bg-primary m-2 px-4 category-badge"; // Bootstrap badge
        categoryBadge.textContent = category;
        // Add event listener to handle category click
        categoryBadge.addEventListener("click", () => {
          selectedCategory = category;
          const badges = document.querySelectorAll('.category-badge');
          badges.forEach((badge, index) => {
            badge.style.setProperty("background-color", "#5226b9", "important");
          });
          categoryBadge.style.setProperty("background-color", "#d55a90", "important");
          //alert(`display arabic news by category ${category}`)
        });
        categoryContainer.appendChild(categoryBadge);
      });
    }
  });
  // Fetch all categories
  async function fetchCategories() {
    try {
      const response = await fetch(`${BASE_URL}/get_ar_category`);
      if (!response.ok) {
        throw new Error(`Error fetching categories: ${response.statusText}`);
      }
      const data = await response.json();
      console.log("Categories:", data);
      return data;
    } catch (error) {
      console.error(error);
    }
  }
  // Fetch news by category
  async function fetchNewsByCategory(categoryId, maxReturnNews = 9) {
    try {
      const response = await fetch(
        `${BASE_URL}/get_ar_news_by_category?category_id=${categoryId}&max_return_news=${maxReturnNews}`
      );
      if (!response.ok) {
        throw new Error(
          `Error fetching news by category: ${response.statusText}`
        );
      }
      const data = await response.json();
      console.log(`News in category ${categoryId}:`, data);
      return data;
    } catch (error) {
      console.error(error);
    }
  }
  // Function to call the backend and get recent news based on the selected categories and subcategories
  async function fetchRecentNews(selections) {
    const button = document.getElementById("getSelectedButton");
    const spinner = document.getElementById("buttonSpinner");
    const newsContainer = document.getElementById("newsContainer");
    try {
      // Show the spinner
      spinner.classList.remove("d-none");
      button.setAttribute("disabled", true); // Disable the button to prevent multiple clicks
      const response = await fetch("/get_recent_news", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(selections), // Send the list of selected categories and subcategories
      });
      // Check if the response status is OK (status code 200-299)
      if (!response.ok) {
        const errorText = await response.text(); // Try to read the response text for debugging
        console.error("Server returned an error:", errorText);
        throw new Error(`Error: ${response.statusText}`);
      }
      // Try to parse the JSON response
      const newsData = await response.json();
      globalNewsData = newsData;
      // Display the news on the page
      displayNews(newsData);
      // Scroll to the news section with an offset to show more space at the top
      const offset = 100; // Adjust this value as needed (e.g., 100px)
      const newsContainerPosition =
        newsContainer.getBoundingClientRect().top + window.pageYOffset - offset;
      // Scroll to the calculated position with a smooth effect
      window.scrollTo({ top: newsContainerPosition, behavior: "smooth" });
    } catch (error) {
      console.error("Failed to fetch recent news:", error);
    } finally {
      // Hide the spinner and re-enable the button
      spinner.classList.add("d-none");
      button.removeAttribute("disabled");
    }
  }

  function getBootstrapClass(percentage) {
    if (percentage > 70) {
      return "text-success"; // Green color for success
    } else if (percentage >= 30) {
      return "text-warning"; // Yellow color for warning
    } else {
      return "text-danger"; // Red color for danger
    }
  }
  // Function to display the retrieved news as Bootstrap cards, with 3 cards per row
  function displayNews(newsData) {
    const newsContainer = document.getElementById("newsContainer");
    newsContainer.innerHTML = ""; // Clear any previous news
    if (newsData.length === 0) {
      newsContainer.innerHTML = `
        <div class="alert alert-warning w-100 text-center" role="alert">
          No news articles found for the selected categories.
        </div>
        `;
      return;
    }
    let row;
    newsData.forEach((news, index) => {
      // Every time we start a new row (index % 3 === 0), create a new row div
      if (index % 3 === 0) {
        row = document.createElement("div");
        row.className = "row mb-3"; // Bootstrap row with margin-bottom
        newsContainer.appendChild(row);
      }
      // Create a new card for each news item
      const card = document.createElement("div");
      card.className = "col-md-4"; // Each card should take 4 columns (1/3 of a row)
      // Card inner HTML with a fixed height and text truncation for abstract
      var percentage = Math.round(news.confidence*100);
      card.innerHTML = `
          <div class="card h-100">
              <div class="card-body">
                  <h5 class="card-title">${truncateText(
                    news.title,
                    maxLengthTtile
                  )}</h5>
                  <p class="card-text card-abstract">${truncateText(
                    news.content,
                    maxLengthAbstract
                  )}</p>
                  <div class="small my-2 p-3" style="border: 1px dashed #6bb0f9; border-radius: 12px; color: #6bb0f9;">
                    <img class="ai-icon" src="static/img/ai-icon.svg" alt="ai-icon">
                    AI-Categorized (<span class="${getBootstrapClass(percentage)}">${percentage}%</span>)
                  </div>
                  <span class="badge text-bg-secondary px-4 category-badge-tag">
                    ${news.predicted_category} 
                  </span>
              </div>
              <div class="card-footer">
                <button type="button" class="btn btn-news-read-more" data-news-id="${
                  news.id
                }">Read more</button>
              </div>
          </div>
      `;
      // Append the card to the current row
      row.appendChild(card);
    });
    // Function to attach click handlers to all buttons with class 'btn-news-read-more'
    document.querySelectorAll(".btn-news-read-more").forEach(function (button) {
      button.addEventListener("click", function () {
        displayNewsModal(button);
      });
    });
  }
  // fucntion to display the news in modal
  function displayNewsModal(newsItem) {
    prepareNewsModal(newsItem);
    newsModal.show();
  }
  // function to extract news detail and update modal html
  function prepareNewsModal(newsItem) {
    // Get the data-user-id attribute from the clicked button
    const newsId = newsItem.getAttribute("data-news-id");
    const news = getNewsById(newsId);
    console.log("found news",news);
    
    document.getElementById("modalNewsTitle").innerHTML = news.title;
    document.getElementById("modalNewsAbstract").innerHTML = news.content;
    // populate the ai recommendation
    updateAiSummarizationModalSection(newsId);
  }
  // function to get news detail from the initial news list
  function getNewsById(newsId) {
    return globalNewsData.find(function (obj) {
      return obj.id == newsId;
    });
  }
  // function to get the ai recommeded news based on id of news
  async function getAiRecommendedNews(newsId) {
    // get similar news from AI model
    getSimilarArticles(newsId).then((similarArticles) => {
      if (similarArticles) {
        // add the to global news array
        globalNewsData.push(...similarArticles);
        updateAiRecommendationModalSection(similarArticles);
      }
    });
  }
  // function that update model section with ai remmended news
  function updateAiSummarizationModalSection(id) {
    const container = document.getElementById("aiSummarizationNewsContainer");
    container.innerHTML = `
    <div class="d-flex justify-content-center">
      <div class="spinner-border" role="status" style="width: 5rem; height: 5rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    `;
    summarizeNewsById(id).then(function(summarizedContent){
      container.innerHTML = summarizedContent.summary;
    })
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
      return data
  } catch (error) {
      console.error(error);
  }
}
  // function to truncate text based on max number of chars
  function truncateText(text, max) {
    if (text.length > max) {
      return text.substring(0, max) + "...";
    }
    return text;
  }
  async function getSimilarArticles(articleId) {
    const url = "/get_similar_articles"; // Adjust the URL to your server's address
    const requestData = {
      article_id: articleId,
    };
    try {
      const response = await fetch(url, {
        method: "POST", // POST method
        headers: {
          "Content-Type": "application/json", // Set the request header
        },
        body: JSON.stringify(requestData), // Send the JSON request body
      });
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error:", errorData);
        return;
      }
      const data = await response.json();
      console.log("Similar Articles:", data.similar_articles);
      return data.similar_articles; // Return the similar articles if needed
    } catch (error) {
      console.error("Network error:", error);
    }
  }
  // Retrieve or create and return the unique number
  const uniqueNumber = getOrCreateUniqueNumber();
  console.log("Unique Number:", uniqueNumber);
};
