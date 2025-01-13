import google.generativeai as genai

genai.configure(api_key="AIzaSyCqpRCumeh9oQxSXbD5QHQDfSkO-9XlKww")

# Function to process DeepFace results and send them to Gemini for activity suggestions
def suggest_activity(deepface_result):
    try:
        # Create a Gemini model instance
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")

        # Extract relevant fields from DeepFace result
        emotion = deepface_result.get('dominant_emotion', 'unknown')
        emotion_percentages = deepface_result.get('emotion', {})
        gender = deepface_result.get('dominant_gender', 'unknown')
        face_confidence = deepface_result.get('face_confidence', 'unknown')
        age = deepface_result.get('age', 'unknown')

        # Validate extracted fields      
        if not emotion or not emotion_percentages or not gender:
            return "Insufficient information to suggest an activity."

        # Convert the emotion percentages to a readable format
        emotion_str = ", ".join([f"{key}: {value:.2f}%" for key, value in emotion_percentages.items()])

        prompt = (f"Based on the following information, suggest an activity:\n"
                  f"Dominant Emotion: {emotion}\n"
                  f"Emotion Percentages: {emotion_str}\n"
                  f"Gender: {gender}\n"
                  f"Face Confidence: {face_confidence}\n"
                  f"Age: {age}\n"
                  "Please suggest one suitable activity based on this person's emotions. "
                  "Only return one activity, and 2 to **********"+emotion_str)
       
        prompt = (f"Based on the following information, suggest an activity:\n"
                  f"Dominant Emotion: {emotion}\n"
                  f"Emotion Percentages: {emotion_str}\n"
                  f"Gender: {gender}\n"
                  f"Face Confidence: {face_confidence}\n"
                  f"Age: {age}\n"
                  "Please suggest one suitable activity based on this person's emotions. "
                  "Only return one activity, and 2 to 3 line discription of it.do not related this responce to preivous")

        # Generate content using the model
        response = model.generate_content(prompt)

        # Extract and return the suggested activity
        if response.candidates and len(response.candidates) > 0:
            suggestion = response.candidates[0].content.parts[0].text
            return suggestion.strip()  # Return the suggested activity
        else:
            return "No suggestion available in the response."

    except Exception as e:
        return f"Exception occurred: {str(e)}"