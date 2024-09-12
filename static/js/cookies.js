// Function to generate a unique number
function generateUniqueNumber() {
    return Date.now() + Math.floor(Math.random() * 1000);
  }
  
  // Function to set a cookie
  function setCookie(name, value, days) {
    let expires = "";
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
  }
  
  // Function to get a cookie by name
  function getCookie(name) {
    const nameEQ = name + "=";
    const cookiesArray = document.cookie.split(';');
    
    for (let i = 0; i < cookiesArray.length; i++) {
      let cookie = cookiesArray[i].trim();
      if (cookie.indexOf(nameEQ) === 0) {
        return cookie.substring(nameEQ.length, cookie.length);
      }
    }
    
    return null;
  }
  
  // Function to retrieve the unique number or create a new one if it doesn't exist
  export function getOrCreateUniqueNumber() {
    let uniqueNumber = getCookie("uniqueNumber");
    
    if (!uniqueNumber) {
      // If no cookie found, generate a new unique number
      uniqueNumber = generateUniqueNumber();
      setCookie("uniqueNumber", uniqueNumber, 7); // Store it for 7 days
    }
    
    return uniqueNumber;
  }
