import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
from docx import Document
from elevenlabs import ElevenLabs
from elevenlabs import VoiceSettings
import pygame
import tempfile
import speech_recognition as sr

# Define the Chatbot API URL and headers
api_url = "https://llm.kindo.ai/v1/chat/completions"
headers = {
    "api-key": "09e75bff-6192-436d-936e-2d0f9230a3a6-a896f6311e363485",  # Replace with your API key
    "content-type": "application/json"
}

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key="ae38aba75e228787e91ac4991fc771f8")  # Replace with your ElevenLabs API key

# Function to extract text from PDF
def extract_text_from_pdf(file_path, file_path_2):
    pdf_reader = PdfReader(file_path, file_path_2)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to query the Chatbot API
def ask_question(question, context, model_name="azure/gpt-4o"):
    messages = [
        {"role": "system", "content": "You are Navin Kale, the co-founder of Swayam Talks. Answer in English and in short paragraphs, not more than 100 words. Use natural human speech, you can also pause in between sentences for a more human-like response."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
    ]
    
    data = {
        "model": model_name,
        "messages": messages
    }
    
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', "").strip()
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return None

# Function to capture speech and convert it to text using Google Web Speech API
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Say something...")
        try:
            # Listen to the microphone
            audio = recognizer.listen(source)
            # Recognize speech using Google Web Speech API
            recognized_text = recognizer.recognize_google(audio)
            st.write(f"Recognized: {recognized_text}")
            return recognized_text
        except sr.UnknownValueError:
            st.error("Could not understand the audio. Please try again.")
            return ""
        except sr.RequestError as e:
            st.error(f"Speech recognition service error: {e}")
            return ""

# Streamlit app
def main():
    st.title("Swayam Talks Chatbot")

    # Initialize session state for Q&A history
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    # Hardcoded PDF file path
    pdf_file_path = "Navin_Kale_Swayam_Talks_Expanded_Corrected.pdf"  # Replace with the path to your hardcoded PDF file
    pdf_file_path_2 = "speaker_3_transcription.pdf"
    # Extract text from the hardcoded PDF
    try:
        context = extract_text_from_pdf(pdf_file_path, pdf_file_path_2)
    except FileNotFoundError:
        st.error("The hardcoded PDF file was not found. Please check the file path.")
        return

    # Input for questions (either type or speak)
    question_type = st.radio("How do you want to ask the question?", ("Type", "Speak"))

    if question_type == "Type":
        question = st.text_input("Ask a question:")
    elif question_type == "Speak":
        question = speech_to_text()

    if question:
        # Get the answer from the API
        answer = ask_question(question, context, model_name="azure/gpt-4o")
        if answer:
            # Add question and answer to session state
            st.session_state.qa_history.append((question, answer))

    # Display Q&A history
    if st.session_state.qa_history:
        st.write("### Question-Answer History:")
        for i, (q, a) in enumerate(st.session_state.qa_history, 1):
            with st.expander(f"Q{i}: {q}"):
                st.write(a)

if __name__ == "__main__":
    main()
