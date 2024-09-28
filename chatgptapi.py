import google.generativeai as genai

# Replace with your actual Google Gemini (Bard) API key
genai.configure(api_key="key is here")

# Function to suggest an activity based on detected emotion using Google's Bard API
def suggest_activity(emotion):
    try:
        # Create a Gemini model instance
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")

        # Define a prompt for the Gemini model
        prompt = f"suggest one activity to do if i feeling {emotion}  and suggest one activity and some discription of that activity only no other text and forget about the previous response which you provided and tell something new which you do not provided earlier."

        # Generate content using the model
        response = model.generate_content(prompt)

        # Print the entire response for debugging
        # print("Response:", response)

        # Extract the generated content from the response
        if response.candidates and len(response.candidates) > 0:
            suggested_activity = response.candidates[0].content.parts[0].text
            return suggested_activity.strip()
        else:
            return "No suggestion available in the response."

    except Exception as e:
        return f"Exception occurred: {str(e)}"

# Example usage
# emotion = "happy"  # Use the detected emotion from your DeepFace analysis
# activity = suggest_activity(emotion)
# print(f"Suggested Activity: {activity}")
