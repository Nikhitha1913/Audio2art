import speech_recognition as sr
from PIL import Image
import requests
from io import BytesIO
import streamlit as st

# Function to transcribe audio to text using Speech Recognition
def audio_to_text():
    recognizer = sr.Recognizer()
    
    # Set timeout for the recognition operation
    recognizer.operation_timeout = 10  # Timeout after 10 seconds
    
    # Record audio from the microphone
    with sr.Microphone() as source:
        st.write("Listening for your prompt...")
        # Add a short pause to adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
        
    # Recognize the speech using Google's speech recognition
    try:
        prompt = recognizer.recognize_google(audio)
        st.write(f"Transcribed text: {prompt}")
        return prompt
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        st.error("Could not request results from Google Speech Recognition.")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# Function to generate image from text prompt using Hugging Face's Inference API
def generate_image_from_text(prompt):
    try:
        # The Stable Diffusion XL model on Hugging Face
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        
        # Your Hugging Face token
        headers = {"Authorization": "Bearer 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"}
        
        # Make request to the Hugging Face API
        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Check if the response contains an error
        if response.status_code != 200:
            st.error(f"Error from Hugging Face API: {response.text}")
            return None
            
        # Get image from the response
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Error generating image: {e}")
        st.error(f"Details: {str(e)}")
        return None

# Streamlit App Layout
st.title("Audio to Art App")
st.write("Speak a prompt to generate a visual masterpiece!")

# Add a status indicator
status = st.empty()

if st.button('Start Listening'):
    status.info("Listening...")
    # Convert audio to text
    prompt_text = audio_to_text()
    
    if prompt_text:
        status.info(f"Prompt received: {prompt_text}")
        
        # Generate image from the prompt
        status.info("Generating image...")
        generated_image = generate_image_from_text(prompt_text)
        
        if generated_image:
            status.empty()
            st.image(generated_image, caption='Generated Image', use_column_width=True)
        else:
            status.error("Failed to generate image")
    else:
        status.error("No prompt detected")
