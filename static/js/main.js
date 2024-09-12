console.log("Main JS is running...");
// Import a function from cookies.js
import { getOrCreateUniqueNumber } from "./cookies.js";
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

  // Function to create and display Bootstrap badges
  function createBadges(categories) {
    const badgeContainer = document.getElementById("badge-container");

    // Clear the container before adding new badges (if needed)
    badgeContainer.innerHTML = "";

    categories.forEach((categoryObj) => {
      // Create a category badge
      const categoryBadge = document.createElement("span");
      categoryBadge.className = "badge bg-primary m-1"; // Bootstrap badge classes
      categoryBadge.textContent = categoryObj.category; // Set the category name as the badge text

      // Append the category badge to the container
      badgeContainer.appendChild(categoryBadge);

      // Create sub-category badges
      const subCategoryDiv = document.createElement("div");
      subCategoryDiv.className = "sub-category-container my-2";

      categoryObj.sub_category.forEach((subCategory) => {
        const subCategoryBadge = document.createElement("span");
        subCategoryBadge.className = "badge bg-secondary m-1"; // Bootstrap badge classes for sub-categories
        subCategoryBadge.textContent = subCategory; // Set sub-category text

        // Append each sub-category badge to the subCategoryDiv
        subCategoryDiv.appendChild(subCategoryBadge);
      });

      // Append the sub-category badges under the category badge
      badgeContainer.appendChild(subCategoryDiv);
    });
  }

  // Fetch the categories and create badges when the page loads
  get_category().then(function (response) {
    if (response) {
      createBadges(response); // Pass the categories to the badge creation function
    }
  });
  // Retrieve or create and return the unique number
  const uniqueNumber = getOrCreateUniqueNumber();
  console.log("Unique Number:", uniqueNumber);
};
