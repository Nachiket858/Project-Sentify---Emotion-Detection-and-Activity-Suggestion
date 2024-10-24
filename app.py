import cv2
import numpy as np
from deepface import DeepFace
from flask import Flask, Response, render_template, jsonify, request
from bard import suggest_activity

app = Flask(__name__)

# Global variables for storing the last detected emotion, gender, and activity
last_emotion = None
last_gender = None
last_activity = None

# Initialize the webcam as None
cap = None

# Helper function to initialize the camera
def initialize_camera():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open webcam")

# Helper function to release the camera
def release_camera():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()

# Route for mode selection page
@app.route('/')
@app.route('/mode_selection')
def mode_selection():
    release_camera()  # Release the camera when switching modes
    return render_template('mode_selection.html')

# Route for camera mode
@app.route('/camera')
def camera():
    initialize_camera()  # Re-initialize the camera when switching to camera mode
    return render_template('camera.html')

# Route for image upload mode
@app.route('/upload')
def upload():
    release_camera()  # Release the camera when switching to upload mode
    return render_template('upload.html')

# Generate frames from the webcam for live video feed
def generate_frames():
    global last_emotion, last_gender, last_activity
    initialize_camera()  # Ensure the camera is initialized before generating frames

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces using Haar Cascade
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Draw rectangles around detected faces and display emotion
            for (x, y, w, h) in faces:
                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Display detected emotion on the frame if available
                if last_emotion:
                    cv2.putText(frame, f"Emotion: {last_emotion}", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

            # Encode frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame as a byte stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route to detect emotion in camera mode
@app.route('/detect_emotion', methods=['POST'])
def detect_emotion():
    global last_emotion, last_gender, last_activity
    
    try:
        success, frame = cap.read()
        if not success:
            return jsonify({"message": "Could not capture frame"})

        result = DeepFace.analyze(frame, actions=['emotion', 'gender'], enforce_detection=False)
        last_emotion = result[0]['dominant_emotion']
        last_gender = result[0]['dominant_gender']
        last_activity = suggest_activity(result[0])

        return jsonify({
            "message": "Emotion detection successful", 
            "emotion": last_emotion, 
            "gender": last_gender, 
            "activity": last_activity
        })
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"})

# Route to detect emotion in uploaded image
@app.route('/upload_image', methods=['POST'])
def upload_image():
    global last_emotion, last_gender, last_activity
    
    try:
        file = request.files['file']
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        result = DeepFace.analyze(img, actions=['emotion', 'gender'], enforce_detection=False)
        last_emotion = result[0]['dominant_emotion']
        last_gender = result[0]['dominant_gender']
        last_activity = suggest_activity(result[0])

        return jsonify({
            "message": "Image uploaded successfully", 
            "emotion": last_emotion, 
            "gender": last_gender, 
            "activity": last_activity
        })
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"})

# Run the app
# if __name__ == "__main__":
#     app.run(debug=True)
if __name__ == "__main__":
    app.run(debug= False, host = '0.0.0.0')