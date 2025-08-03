# google_tts_service.py
from gtts import gTTS
import os
import hashlib
import threading
import time

# Cache için gelişmiş sistem
_audio_cache = {}
_cache_lock = threading.Lock()

def generate_google_tts(text, filename="output.mp3", lang="en", voice_name=None):
    """
    Google Text-to-Speech ile verilen metni seslendirip mp3 dosyası olarak kaydeder.
    Optimized for speed.
    """
    # Cache kontrolü - aynı metin için önceden oluşturulmuş dosyayı kullan
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_filename = f"cached_{text_hash}.mp3"
    
    # Create audio directory
    audio_dir = os.path.join("static", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    cache_path = os.path.join(audio_dir, cache_filename)
    
    # Thread-safe cache kontrolü
    with _cache_lock:
        if text_hash in _audio_cache:
            print(f"Using memory cached audio: {cache_filename}")
            return cache_path
    
    # Eğer cache'de varsa, onu kullan
    if os.path.exists(cache_path):
        print(f"Using disk cached audio: {cache_filename}")
        with _cache_lock:
            _audio_cache[text_hash] = cache_path
        return cache_path
    
    # Yeni ses dosyası oluştur - daha hızlı ayarlar
    print(f"Generating new audio for: {text[:30]}...")
    
    # Daha kısa metinler için hızlı ayarlar
    if len(text) < 100:
        tts = gTTS(text=text, lang=lang, slow=False)
    else:
        # Uzun metinler için normal ayarlar
        tts = gTTS(text=text, lang=lang, slow=False)
    
    # Cache dosyasına kaydet
    try:
        tts.save(cache_path)
        print(f"Audio saved: {cache_filename}")
        
        # Memory cache'e ekle
        with _cache_lock:
            _audio_cache[text_hash] = cache_path
            
        return cache_path
    except Exception as e:
        print(f"TTS Error: {e}")
        # Fallback - boş dosya oluştur
        with open(cache_path, 'w') as f:
            pass
        return cache_path

def preload_common_audio():
    """Yaygın kullanılan ses dosyalarını önceden yükle"""
    common_texts = [
        "Hello, how can I help you?",
        "Thank you for calling.",
        "Please hold the line.",
        "I'll transfer you now."
    ]
    
    print("Preloading common audio files...")
    for text in common_texts:
        generate_google_tts(text, f"common_{hash(text) % 1000}.mp3")

# Örnek kullanım:
if __name__ == "__main__":
    sample_text = """
    Hi, everyone. I know you're all busy so I'll keep this briefing quick.
    Our head of department, James Watson, is leaving his position at the end of this week.
    The car park will be closed next month, but we can use the church parking.
    """
    generate_google_tts(sample_text, filename="staff_briefing.mp3") 