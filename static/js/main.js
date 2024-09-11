console.log("Main JS is running...");
window.onload = function() {
    console.log("Page has fully loaded!");
    // Function to add a new user
document.getElementById('userForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const age = document.getElementById('age').value;
    const city = document.getElementById('city').value;
    
    // Send user data to Flask API
    const response = await fetch('/add_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            age: age,
            city: city
        })
    });
    
    const result = await response.json();
    showTost("Add user", result.message)
    // Refresh the user list
    listUsers();
});

// Function to list all users
async function listUsers() {
    const response = await fetch('/list_users', {
        method: 'GET'
    });
    const users = await response.json();
    
    // Clear the current list
    const userList = document.getElementById('userList');
    userList.innerHTML = '';
    
    // Populate the user list
    users.forEach(user => {
        const li = document.createElement('li');
        li.textContent = `Name: ${user.name}, Age: ${user.age}, City: ${user.city}`;
        userList.appendChild(li);
    });
}

function showTost(title, message){

    var toastElement = document.getElementById('liveToast');

    document.getElementById('toast-title').innerHTML = title;
    document.getElementById('toast-message').innerHTML = message;    
    
    var toast = new bootstrap.Toast(toastElement);
    toast.show();
}
// List users when the page loads
listUsers();
};

