import cv2
import numpy as np
from deepface import DeepFace
from flask import Flask, Response, render_template, jsonify, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from bard import suggest_activity  # Assuming this is a custom module for suggesting activities

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for sessions

# Configure MongoDB with Sentify database
# app.config["MONGO_URI"] = "mongodb://localhost:27017/Sentify"
app.config["MONGO_URI"] = "mongodb+srv://nachiket:pass123@cluster0.bppyd.mongodb.net/Sentify?retryWrites=true&w=majority"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Access the 'users' collection in the 'Sentify' database
users = mongo.db.users

# Global variables for last detected attributes
last_emotion = None
last_gender = None
last_activity = None

# Initialize the webcam
cap = None

def initialize_camera():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open webcam")

def release_camera():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()

# Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Check if username already exists
        existing_user = users.find_one({"username": username})
        
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))
        
        # Hash password and save user
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        users.insert_one({"username": username, "password": hashed_password})
        
        flash("Registration successful! You can now log in.")
        return redirect(url_for("login"))
    
    return render_template("register.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = users.find_one({"username": username})
        
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            flash("Login successful!")
            return redirect(url_for("mode_selection"))
        
        flash("Invalid username or password.")
        return redirect(url_for("login"))
    
    return render_template("login.html")

# Mode Selection Route (formerly dashboard)
@app.route('/')
@app.route('/mode_selection')
def mode_selection():
    if "user_id" not in session:
        flash("You need to log in first.")
        return redirect(url_for("login"))
    
    # Fetch the user's data from the database using the session's user_id
    user = users.find_one({"_id": ObjectId(session["user_id"])})
    
    # Release the camera if needed
    release_camera()
    
    # Pass the username to the template
    return render_template('mode_selection.html', username=user["username"])


# Camera Mode Route
@app.route('/camera')
def camera():
    initialize_camera() 
    return render_template('camera.html')

# Image Upload Mode Route
@app.route('/upload')
def upload():
    release_camera()  
    return render_template('upload.html')

# Generate frames from the webcam for live video feed
def generate_frames():
    global last_emotion, last_gender, last_activity
    initialize_camera()  

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces using Haar Cascade
            faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                if last_emotion:
                    cv2.putText(frame, f"Emotion: {last_emotion}", (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Emotion detection from live feed
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

# Upload image for emotion analysis
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

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully.")
    return redirect(url_for("login"))

# Run the app
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
