import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
import speech_recognition as sr
from gtts import gTTS
import requests

# Function to connect to Azure OpenAI for text correction
def correct_transcription(transcript):
    api_key = "22ec84421ec24230a3638d1b51e3a7dc"  # Your Azure OpenAI API key
    endpoint = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        "messages": [
            {"role": "user", "content": f"Correct the following text for grammatical errors: {transcript}"}
        ]
    }

    response = requests.post(endpoint, headers=headers, json=data)
    corrected_text = response.json()['choices'][0]['message']['content']
    return corrected_text

# Function to transcribe audio from the video
def transcribe_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path)
    
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)  # read the entire audio file

    try:
        transcript = recognizer.recognize_google(audio)
        return transcript
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# Function to generate audio from text using gTTS
def generate_audio(text):
    tts = gTTS(text=text, lang='en')
    audio_path = "output_audio.mp3"
    tts.save(audio_path)
    return audio_path

# Function to replace audio in the video
def replace_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(audio_path)
    final_video = video.set_audio(new_audio)
    final_video_path = "final_video.mp4"
    final_video.write_videofile(final_video_path, codec='libx264', audio_codec='aac')
    return final_video_path

# Streamlit UI
st.title("Video Audio Replacement with AI Voice")
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Transcribe audio from video
    transcript = transcribe_audio(video_path)
    st.write("Transcript:", transcript)

    # Correct the transcription using Azure OpenAI
    corrected_text = correct_transcription(transcript)
    st.write("Corrected Transcript:", corrected_text)

    # Generate AI voice from corrected text
    audio_path = generate_audio(corrected_text)
    st.audio(audio_path)

    # Replace audio in video
    final_video_path = replace_audio(video_path, audio_path)
    st.video(final_video_path)
