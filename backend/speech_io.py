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
            print("Listening for an answer...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout)
        try:
            answer = recognizer.recognize_google(audio)
            print(f"Candidate said: {answer}")
            return answer
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""


