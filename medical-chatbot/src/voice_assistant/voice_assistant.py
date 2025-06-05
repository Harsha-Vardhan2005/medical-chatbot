import pyttsx3
import speech_recognition as sr
import threading

def speak_text(text):
    """Speak out the given text using TTS in a separate thread with reinitialization to avoid issues."""
    def run_speech():
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 220) 
        tts_engine.setProperty('volume', 1) 
        
        tts_engine.say(text)
        tts_engine.runAndWait()
        tts_engine.stop()

    speech_thread = threading.Thread(target=run_speech)
    speech_thread.start()

def stop_speaking():
    """Stop speaking immediately."""
    tts_engine = pyttsx3.init()
    tts_engine.stop()

def listen_for_voice_input():
    """Listen to the microphone and convert speech to text using STT."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice input...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio_data = recognizer.listen(source)

    try:
        # Convert audio to text
        user_input = recognizer.recognize_google(audio_data)
        print(f"Recognized voice input: {user_input}")
        return user_input
    except sr.UnknownValueError:
        print("Could not understand audio")
        return "Sorry, I didn't catch that."
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return "Sorry, there was an error with the voice service."
