// Function to check for internet connection
function isConnected() {
    return fetch('https://www.google.com', { method: 'HEAD', mode: 'no-cors' })
        .then(() => true)
        .catch(() => false);
}

// Function to preview image and automatically detect emotion
function previewImageAndDetectEmotion(event) {
    const image = document.getElementById('uploadedImage');
    image.src = URL.createObjectURL(event.target.files[0]);
    image.style.display = 'block'; // Show the image

    // Show animation for image upload
    image.style.animation = 'fadeIn 0.5s'; // Add fade-in animation

    // Automatically call the detect emotion function after image preview
    isConnected().then(connected => {
        if (connected) {
            detectEmotion();
        } else {
            alert("No internet connection. Please check your connection and try again.");
        }
    });
}

// Function to upload image and detect emotion
function detectEmotion() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    let fileInput = document.getElementById('imageInput');
    let formData = new FormData();
    formData.append('file', fileInput.files[0]);

    loadingIndicator.style.display = 'block'; // Show loading indicator

    fetch('/upload_image', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            // Display the detected emotion, gender, and activity
            document.getElementById('emotionText').innerText = `Detected Emotion: ${data.emotion}`;
            document.getElementById('genderText').innerText = `Detected Gender: ${data.gender}`;
            document.getElementById('activityText').innerText = `Suggested Activity: ${data.activity}`;
            
            // Show the image with detected emotion and a rectangle around the face
            if (data.image_with_emotion) {
                document.getElementById('uploadedImage').src = `data:image/jpeg;base64,${data.image_with_emotion}`;
            }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => {
            loadingIndicator.style.display = 'none'; // Hide loading indicator after processing
        });
}

// Function to switch to Camera Mode
function switchMode() {
    window.location.href = '/camera'; // Redirect to camera mode
}