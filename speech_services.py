# speech_services.py
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os

def listen_to_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dinleniyor...")
        r.pause_threshold = 1
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language='en-US')
            print(f"Kullanıcı dedi ki: {text}")
            return text
        except sr.UnknownValueError:
            speak_text("Sorry, I did not understand that. Could you please repeat?")
            return None
        except sr.RequestError:
            speak_text("Sorry, my speech service is down.")
            return None

def speak_text(text):
    print(f"Yapay Zeka diyor ki: {text}")
    tts = gTTS(text=text, lang='en', tld='co.uk', slow=False) # IELTS için İngiliz aksanı (tld='co.uk') daha doğal olabilir
    filename = "temp_audio.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)