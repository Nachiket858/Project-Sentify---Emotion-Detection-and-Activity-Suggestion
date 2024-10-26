// Function to check for internet connection
function isConnected() {
    return fetch('https://www.google.com', { method: 'HEAD', mode: 'no-cors' })
        .then(() => true)
        .catch(() => false);
}

// Function to detect emotion by calling the backend endpoint
function detectEmotion() {
    document.getElementById('loading').style.display = 'block'; // Show loading
    fetch('/detect_emotion', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('emotionText').innerText = `Detected Emotion: ${data.emotion}`;
            document.getElementById('genderText').innerText = `Detected Gender: ${data.gender}`;
            document.getElementById('activityText').innerText = `Suggested Activity: ${data.activity}`;
            document.getElementById('loading').style.display = 'none'; // Hide loading
        })
        .catch(error => {
            alert("Error detecting emotion. Please try again.");
            document.getElementById('loading').style.display = 'none'; // Hide loading
        });
}

// Automatically detect emotion every 15 seconds
function detectEmotionPeriodically() {
    isConnected().then(connected => {
        if (connected) {
            detectEmotion();
        } else {
            alert("No internet connection. Please check your connection.");
        }
    });
}

// Call the function every 15 seconds
setInterval(detectEmotionPeriodically, 15000);

// Function to switch to Image Upload Mode
function switchToUploadMode() {
    window.location.href = "/upload";  // Redirect to the Image Upload page
}

// Initial emotion detection when the page loads
detectEmotionPeriodically();
