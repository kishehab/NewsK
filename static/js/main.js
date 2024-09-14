console.log("Main JS is running...");
// Import a function from cookies.js
import { getOrCreateUniqueNumber } from "./cookies.js";
import { CategoryManager } from './CategoryManager.js'; // Import CategoryManager

window.onload = function () {
  console.log("Page has fully loaded!");
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
  function showTost(title, message) {
    var toastElement = document.getElementById("liveToast");
    document.getElementById("toast-title").innerHTML = title;
    document.getElementById("toast-message").innerHTML = message;
    var toast = new bootstrap.Toast(toastElement);
    toast.show();
  }
  // Fetch the categories and sub-categories from the server
  async function get_category() {
    try {
      // Show the skeleton loader
      showSkeletonLoader();

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
      // Hide the skeleton loader
      hideSkeletonLoader();
    }
  }

  // Function to show the skeleton loader
  function showSkeletonLoader() {
    const skeletonContainer = document.getElementById("skeleton-container");
    const badgeContainer = document.getElementById("badge-container");

    // Show skeleton loader and hide badge container
    skeletonContainer.classList.remove("d-none");
    badgeContainer.classList.add("d-none");
  }

  // Function to hide the skeleton loader
  function hideSkeletonLoader() {
    const skeletonContainer = document.getElementById("skeleton-container");
    const badgeContainer = document.getElementById("badge-container");

    // Hide skeleton loader and show badge container
    skeletonContainer.classList.add("d-none");
    badgeContainer.classList.remove("d-none");
  }

 // main.js


const categoryManager = new CategoryManager();

// Fetch the categories and sub-categories from the server
async function get_category() {
    try {
        const response = await fetch('/get_category', {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching category:', error);
        alert('Failed to fetch categories');
    }
}

// Function to display categories
function displayCategories() {
    const categoryContainer = document.getElementById('category-container');
    categoryContainer.innerHTML = ''; // Clear the container

    categoryManager.categories.forEach(category => {
        const categoryBadge = document.createElement('span');
        categoryBadge.className = 'badge bg-primary m-2 category-badge'; // Bootstrap badge
        categoryBadge.textContent = category.name;

        // Create a span for the selected subcategory counter
        const counterBadge = document.createElement('span');
        counterBadge.className = 'badge bg-light text-dark m-2';
        counterBadge.textContent = `(${category.getSelectedSubcategoryCount()})`; // Show the initial count as 0

        // Add event listener to handle category click
        categoryBadge.addEventListener('click', () => {
            categoryManager.setSelectedCategory(category.name); // Set selected category
            displaySubcategories(category, counterBadge); // Pass the counterBadge to update the count later
        });

        // Append the category badge and counter to the container
        categoryContainer.appendChild(categoryBadge);
        categoryContainer.appendChild(counterBadge);
    });
}

// Function to display subcategories for the selected category
function displaySubcategories(category, counterBadge) {
    const subcategoryContainer = document.getElementById('subcategory-container');
    subcategoryContainer.innerHTML = ''; // Clear the container
    subcategoryContainer.classList.remove('d-none');

    category.subcategories.forEach(subcategory => {
        const subCategoryBadge = document.createElement('span');
        subCategoryBadge.className = 'badge bg-secondary m-2 subcategory-badge'; // Bootstrap badge
        subCategoryBadge.textContent = subcategory;

        // Check if the subcategory is already selected and add a selected class if true
        if (category.selectedSubcategories.includes(subcategory)) {
            subCategoryBadge.classList.add('selected');
        }

        // Add click event listener to toggle subcategory selection
        subCategoryBadge.addEventListener('click', function () {
            categoryManager.selectedCategory.toggleSubcategory(subcategory); // Toggle selection

            // Toggle visual indication of selection
            this.classList.toggle('selected');

            // Update the subcategory counter
            counterBadge.textContent = `(${category.getSelectedSubcategoryCount()})`;

            // Log the selected category and subcategories
            console.log('Selected category:', categoryManager.getSelectedCategoryInfo());
        });

        // Append the subcategory badge to the container
        subcategoryContainer.appendChild(subCategoryBadge);
    });
}

// Fetch categories and initialize the page
get_category().then(function(response) {
    if (response) {
        response.forEach(cat => {
            categoryManager.addCategory(cat.category, cat.sub_category); // Add categories to manager
        });

        displayCategories(); // Display categories
    }
});


  // Retrieve or create and return the unique number
  const uniqueNumber = getOrCreateUniqueNumber();
  console.log("Unique Number:", uniqueNumber);
};
