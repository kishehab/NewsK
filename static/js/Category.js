// category.js

export class Category {
    constructor(name, subcategories) {
        this.name = name; // The category name
        this.subcategories = subcategories; // List of subcategories
        this.selectedSubcategories = []; // Subcategories that are selected by the user
    }

    // Function to toggle a subcategory selection
    toggleSubcategory(subcategory) {
        if (this.selectedSubcategories.includes(subcategory)) {
            this.selectedSubcategories = this.selectedSubcategories.filter(sub => sub !== subcategory);
        } else {
            this.selectedSubcategories.push(subcategory);
        }
    }

    // Function to return the selected subcategories
    getSelectedSubcategories() {
        return this.selectedSubcategories;
    }

    // Function to return the count of selected subcategories
    getSelectedSubcategoryCount() {
        return this.selectedSubcategories.length;
    }
}
