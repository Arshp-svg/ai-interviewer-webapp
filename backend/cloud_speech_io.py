"""
Simplified audio handler that definitely works
"""
import streamlit as st
import speech_recognition as sr
import io
import numpy as np

class CloudSpeechIO:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Optimize recognizer settings for better performance
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
    
    def speak(self, text):
        """Text-to-speech functionality"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except:
            # Fallback: just display text
            st.info(f"🔊 **Question:** {text}")
    
    def listen_for_answer(self, timeout=30):
        """Record audio and convert to text"""
        try:
            from audio_recorder_streamlit import audio_recorder
            
            st.info("🎤 Click the button below to record your answer")
            
            # Simple, reliable audio recording
            audio_bytes = audio_recorder(
                text="🎙️ Record Answer",
                recording_color="#e8b62c",
                neutral_color="#6aa36f",
                key="interview_recorder"
            )
            
            if audio_bytes:
                st.success("✅ Audio recorded!")
                
                # Show audio playback
                st.audio(audio_bytes, format="audio/wav")
                
                # Convert to text
                return self._convert_audio_to_text(audio_bytes)
            
            return None
            
        except ImportError:
            st.warning("⚠️ Audio recording not available. Please type your answer:")
            return self._text_input()
        except Exception as e:
            st.warning(f"⚠️ Recording failed: {str(e)}. Please type your answer:")
            return self._text_input()
    
    def _convert_audio_to_text(self, audio_bytes):
        """Convert audio bytes to text using multiple methods"""
        try:
            st.info("🔄 Converting speech to text...")
            
            # Method 1: Try with librosa for better audio processing (if available)
            try:
                import librosa
                import soundfile as sf
                
                # Load audio using librosa (more robust)
                audio_io = io.BytesIO(audio_bytes)
                
                # Try to read as different audio formats
                try:
                    # Try reading as WAV first
                    y, sr_rate = librosa.load(audio_io, sr=16000, mono=True)
                    
                    # Convert to the format speech_recognition expects
                    # Ensure the audio is in the right format (16-bit PCM)
                    audio_int16 = (y * 32767).astype(np.int16)
                    audio_data = sr.AudioData(audio_int16.tobytes(), 16000, 2)
                    
                    text = self.recognizer.recognize_google(audio_data, language='en-US')
                    
                    if text.strip():
                        st.success(f"🎯 **Your Answer:** {text}")
                        st.info("✅ Processed with advanced audio processing")
                        return text.strip()
                        
                except Exception as e:
                    st.info(f"Advanced method failed: {e}. Trying basic methods...")
                    
            except ImportError:
                st.info("📢 Using basic audio processing (librosa not available)")
            
            # Method 2: Basic approach with multiple sample rates (works without librosa)
            sample_rates = [16000, 44100, 22050, 8000]
            sample_widths = [2, 1]  # Try 16-bit first, then 8-bit
            
            for sr_rate in sample_rates:
                for width in sample_widths:
                    try:
                        audio_data = sr.AudioData(audio_bytes, sr_rate, width)
                        text = self.recognizer.recognize_google(audio_data, language='en-US')
                        
                        if text.strip():
                            st.success(f"🎯 **Your Answer:** {text}")
                            st.info(f"✅ Success with {sr_rate}Hz, {width*8}-bit audio")
                            return text.strip()
                            
                    except Exception as e:
                        continue  # Try next configuration
            
            # Method 3: Try with different language codes
            try:
                # Use most common format as base
                audio_data = sr.AudioData(audio_bytes, 16000, 2)
                
                # Try different language variants
                languages = ['en-US', 'en-GB', 'en-IN', 'en']
                for lang in languages:
                    try:
                        text = self.recognizer.recognize_google(audio_data, language=lang)
                        if text.strip():
                            st.success(f"🎯 **Your Answer:** {text}")
                            st.info(f"✅ Success with language: {lang}")
                            return text.strip()
                    except:
                        continue
                        
            except Exception as e:
                pass
            
            # Method 4: Try adjusting recognizer settings
            try:
                # Temporarily adjust settings for difficult audio
                original_energy = self.recognizer.energy_threshold
                original_pause = self.recognizer.pause_threshold
                
                # Make recognizer more sensitive
                self.recognizer.energy_threshold = 100  # Lower threshold
                self.recognizer.pause_threshold = 0.5   # Shorter pause
                
                audio_data = sr.AudioData(audio_bytes, 22050, 2)
                text = self.recognizer.recognize_google(audio_data, language='en-US')
                
                # Restore original settings
                self.recognizer.energy_threshold = original_energy
                self.recognizer.pause_threshold = original_pause
                
                if text.strip():
                    st.success(f"🎯 **Your Answer:** {text}")
                    st.info("✅ Success with adjusted sensitivity")
                    return text.strip()
                    
            except Exception as e:
                # Restore original settings even if failed
                self.recognizer.energy_threshold = 300
                self.recognizer.pause_threshold = 0.8
            
            # If all methods fail
            st.warning("⚠️ Could not understand the audio. This might be due to:")
            st.warning("• Background noise or unclear speech")
            st.warning("• Microphone volume too low/high") 
            st.warning("• Audio format compatibility issues")
            st.info("💡 **Try these solutions:**")
            st.info("• Speak louder and more clearly")
            st.info("• Move closer to your microphone")
            st.info("• Reduce background noise")
            st.info("• Use the text input below as backup")
            return self._text_input()
                
        except sr.UnknownValueError:
            st.warning("⚠️ Speech not recognized. Please speak more clearly:")
            return self._text_input()
        except sr.RequestError as e:
            st.warning(f"⚠️ Speech service error: {e}. Please type your answer:")
            return self._text_input()
        except Exception as e:
            st.warning(f"⚠️ Audio processing failed: {e}. Please type your answer:")
            return self._text_input()
    
    def _text_input(self):
        """Simple text input fallback"""
        st.markdown("### 📝 Type Your Answer")
        
        answer = st.text_area(
            "Your response:",
            height=120,
            placeholder="Type your detailed answer here...",
            key="text_input_fallback"
        )
        
        if st.button("Submit Answer", type="primary", key="submit_answer"):
            if answer.strip():
                return answer.strip()
            else:
                st.warning("Please enter an answer before submitting.")
                return None
        
        return None

# Compatibility class
class SpeechIO:
    def __init__(self):
        self.handler = CloudSpeechIO()
    
    def speak(self, text):
        return self.handler.speak(text)
    
    def listen_for_answer(self, timeout=30):
        return self.handler.listen_for_answer(timeout)