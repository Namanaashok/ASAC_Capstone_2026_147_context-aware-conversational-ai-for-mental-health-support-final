import pyttsx3
import threading

class TTSEngine:
    def __init__(self):
        # We don't initialize pyttsx3 here because it must be initialized 
        # in the same thread it is run from to avoid COM errors on Windows.
        pass
        
    def _speak_thread(self, text):
        """Runs the TTS engine in a separate thread to prevent blocking Streamlit UI"""
        try:
            engine = pyttsx3.init()
            
            # Optional: Configure voice properties to make it sound more calming
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 30)  # Slower, calmer voice
            
            # Try to select a female voice (often perceived as more soothing for wellness apps)
            voices = engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
                    
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    def speak(self, text):
        """Starts a background thread to speak the text"""
        if not text:
            return
            
        # Clean up text a bit so it doesn't read out markdown symbols like asterisks
        clean_text = text.replace('*', '').replace('#', '')
        
        thread = threading.Thread(target=self._speak_thread, args=(clean_text,))
        thread.daemon = True
        thread.start()
