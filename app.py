import cv2
from deepface import DeepFace
from flask import Flask, Response, render_template, jsonify
from bard import suggest_activity  # Import the ChatGPT API handler

# Initialize Flask app
app = Flask(__name__)

# Initialize webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open webcam")

# Load Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Global variables to store the last detected emotion, gender, and activity suggestion
last_emotion = None
last_gender = None
last_activity = None

# Function to generate frames for the video stream
def generate_frames():
    global last_emotion, last_gender, last_activity

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces using Haar Cascade
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Display detected emotion on the frame if available
                if last_emotion:
                    cv2.putText(frame, f"{last_emotion}", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

            # Encode frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame as a byte stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for video stream
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for triggering emotion detection via button click
@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    global last_emotion, last_gender, last_activity

    try:
        # Capture a single frame from the webcam for detection
        success, frame = cap.read()
        if not success:
            return jsonify({"message": "Could not capture frame"})

        # Analyze the frame for emotions and gender
        result = DeepFace.analyze(frame, actions=['emotion', 'gender'], enforce_detection=False)

        # Extract the dominant emotion and gender
        last_emotion = result[0]['dominant_emotion']
        last_gender = result[0]['dominant_gender']

        # Print the entire DeepFace result to the console
        print(f"***************************************************DeepFace Analysis: {result[0]}")

        # Print additional information from DeepFace result
        # for key, value in result[0].items():
        #     print(f"{key}: {value}")

        # Call the OpenAI/ChatGPT API to get an activity suggestion based on the detected emotion
        last_activity = suggest_activity(result[0])

        

        return jsonify({
            "message": "Emotion detection successful", 
            "emotion": last_emotion, 
            "gender": last_gender, 
            "activity": last_activity
        })

    except Exception as e:
        return jsonify({"message": f"Error in emotion detection: {str(e)}"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
