import google.generativeai as genai

# Replace with your actual Google Gemini (Bard) API key
genai.configure(api_key="")

# Function to process DeepFace results and send them to Gemini for activity suggestions
def suggest_activity(deepface_result):
    try:
        # Create a Gemini model instance
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")

        # Extract relevant fields from DeepFace result
        emotion = deepface_result['dominant_emotion']
        emotion_percentages = deepface_result.get('emotion', {})  # Emotion percentages
        gender = deepface_result['dominant_gender']
        face_confidence = deepface_result.get('face_confidence', 'unknown')  # Optional field
        age = deepface_result.get('age', 'unknown')  # Optional field if included in your analysis
        

        # Convert the emotion percentages to a readable format
        emotion_str = ", ".join([f"{key}: {value:.2f}%" for key, value in emotion_percentages.items()])
        print("*************************************"+emotion_str)
        # Define a prompt for the Gemini model, including emotion percentages
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