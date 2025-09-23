import pyttsx3
import speech_recognition as sr
import tempfile
import os

class SpeechIO:
    
    def speak(self,text):
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def listen_for_answer(self, timeout=15):
        # listen for an answer using the microphone
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            # Remove console logging for security
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
        try:
            answer = recognizer.recognize_google(audio)
            # Remove logging of user speech for privacy
            return answer
        except sr.UnknownValueError:
            # Audio not understood - return empty string silently
            return ""
        except sr.RequestError:
            # Speech service error - return empty string silently
            return ""


