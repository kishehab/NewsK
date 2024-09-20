// categoryManager.js

import { Category } from './Category.js'; // Import the Category class

export class CategoryManager {
    constructor() {
        this.categories = []; // List of all categories
        this.selectedCategory = null; // The currently selected category
    }

    // Function to add a category to the manager
    addCategory(name, subcategories) {
        const category = new Category(name, subcategories);
        this.categories.push(category);
    }

    // Function to set the selected category
    setSelectedCategory(categoryName) {
        this.selectedCategory = this.categories.find(category => category.name === categoryName);
        if (!this.selectedCategory) {
            console.log(`Category ${categoryName} not found!`);
        }
    }

    // Function to get the selected category
    getSelectedCategory() {
        return this.selectedCategory;
    }

    // Function to return the selected category and its subcategories
    getSelectedCategoryInfo() {
        if (!this.selectedCategory) {
            return {
                category: null,
                selectedSubcategories: []
            };
        }

        return {
            category: this.selectedCategory.name,
            selectedSubcategories: this.selectedCategory.getSelectedSubcategories()
        };
    }
    // NEW FUNCTION: Get all selected categories along with their selected subcategories
    getAllSelectedCategories() {
        return this.categories
            .map(category => ({
                category: category.name,
                selectedSubcategories: category.getSelectedSubcategories()
            }))
            .filter(category => category.selectedSubcategories.length > 0); // Only return categories with selected subcategories
    }
}
