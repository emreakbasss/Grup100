# listening_generator.py
import google.generativeai as genai
from config import GEMINI_API_KEY
import json
import re
import hashlib
import os
import time

# Gemini API yapılandırması - Daha hızlı model kullan
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("Gemini API configured successfully")
except Exception as e:
    print(f"Gemini API configuration error: {e}")
    model = None

# Cache için basit sistem
_cache_dir = "cache"
os.makedirs(_cache_dir, exist_ok=True)

def get_cache_key(prompt):
    """Cache key oluştur"""
    return hashlib.md5(prompt.encode()).hexdigest()

def get_cached_response(cache_key):
    """Cache'den yanıt al"""
    cache_file = os.path.join(_cache_dir, f"{cache_key}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None

def save_to_cache(cache_key, response):
    """Yanıtı cache'e kaydet"""
    cache_file = os.path.join(_cache_dir, f"{cache_key}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
    except:
        pass

def get_fallback_response():
    """Fallback yanıt döndür"""
    fallback_responses = [
        {
            "dialogue": [
                "A: Hi, I'm calling about the job vacancy you advertised.",
                "B: Yes, we're still accepting applications until Friday."
            ],
            "question": "When is the application deadline?",
            "options": {"A": "Monday", "B": "Wednesday", "C": "Friday", "D": "Sunday"},
            "answer": "C"
        },
        {
            "dialogue": [
                "A: I'd like to book a table for tonight, around 7 PM.",
                "B: Sure, how many people will be dining with you?"
            ],
            "question": "What time does the customer want to dine?",
            "options": {"A": "6 PM", "B": "7 PM", "C": "8 PM", "D": "9 PM"},
            "answer": "B"
        },
        {
            "dialogue": [
                "A: Do you have any yoga classes for beginners?",
                "B: Yes, we have a gentle yoga class every Tuesday at 6 PM."
            ],
            "question": "When is the beginner yoga class?",
            "options": {"A": "Monday 6 PM", "B": "Tuesday 6 PM", "C": "Wednesday 6 PM", "D": "Thursday 6 PM"},
            "answer": "B"
        },
        {
            "dialogue": [
                "A: I'm looking for a good coffee shop to study in.",
                "B: We have free Wi-Fi and plenty of quiet corners for studying."
            ],
            "question": "What does the customer want to do in the coffee shop?",
            "options": {"A": "Meet friends", "B": "Study", "C": "Work", "D": "Relax"},
            "answer": "B"
        },
        {
            "dialogue": [
                "A: Can you help me find a book about sustainable living?",
                "B: Yes, those are in the environmental section on the second floor."
            ],
            "question": "Where can the customer find books about sustainable living?",
            "options": {"A": "First floor", "B": "Second floor", "C": "Third floor", "D": "Basement"},
            "answer": "B"
        }
    ]
    
    import random
    return random.choice(fallback_responses)

def generate_listening_example():
    # Model kontrolü
    if model is None:
        print("Model not available, using fallback")
        fallback = get_fallback_response()
        return json.dumps(fallback)
    
    # Çeşitli konular için prompt'lar
    topics = [
        "health and fitness",
        "daily coffee shop conversation", 
        "education and study tips",
        "travel planning",
        "restaurant dining",
        "shopping and fashion",
        "technology and gadgets",
        "environment and sustainability",
        "sports and activities",
        "work and career"
    ]
    
    import random
    selected_topic = random.choice(topics)
    
    prompt = f"""
    Create a natural 2-turn IELTS Listening Part 1 dialogue about {selected_topic}. 
    Make it engaging and realistic. Return JSON only:
    {{
        "dialogue": ["A: ...", "B: ..."],
        "question": "...",
        "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
        "answer": "..."
    }}
    
    Examples of good topics:
    - Health: doctor appointments, fitness classes, healthy eating
    - Coffee: ordering drinks, cafe atmosphere, meeting friends
    - Education: course registration, study groups, exam preparation
    - Travel: booking flights, hotel reservations, tourist information
    - Restaurant: making reservations, ordering food, dietary preferences
    - Shopping: finding items, sizes, prices, returns
    - Technology: buying gadgets, troubleshooting, software help
    - Environment: recycling, eco-friendly products, sustainability
    - Sports: joining clubs, equipment, training schedules
    - Work: job interviews, office arrangements, professional development
    """
    
    # Cache kontrolü - devre dışı bırakıldı
    # cache_key = get_cache_key(prompt)
    # cached_response = get_cached_response(cache_key)
    # if cached_response:
    #     print("Using cached response")
    #     return json.dumps(cached_response)
    
    try:
        # Daha hızlı yanıt için generation config
        print(f"Calling Gemini API for topic: {selected_topic}...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,  # Biraz daha yaratıcı
                top_p=0.8,
                top_k=30,  # Daha çeşitli
                max_output_tokens=400,  # Biraz daha uzun
            )
        )
        
        print(f"Gemini response received: {response.text[:100]}...")
        
        # Clean the response text to remove markdown formatting
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]  # Remove "```json"
        elif text.startswith("```"):
            text = text[3:]  # Remove "```"
        
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing "```"
        
        # Parse ve cache'e kaydet
        try:
            parsed = json.loads(text.strip())
            
            # Options formatını kontrol et ve düzelt
            if isinstance(parsed.get('options'), list):
                # List formatını dict formatına çevir
                options_list = parsed['options']
                options_dict = {}
                for i, option in enumerate(options_list):
                    if isinstance(option, str):
                        # "A. ..." formatından "A": "..." formatına çevir
                        if option.startswith(('A.', 'B.', 'C.', 'D.')):
                            key = option[0]
                            value = option[3:].strip()
                            options_dict[key] = value
                        else:
                            # Sadece A, B, C, D key'leri kullan
                            key = chr(65 + i)  # A, B, C, D
                            options_dict[key] = option
                    else:
                        key = chr(65 + i)
                        options_dict[key] = str(option)
                
                parsed['options'] = options_dict
                print(f"Converted options from list to dict: {parsed['options']}")
            
            # save_to_cache(cache_key, parsed)  # Cache devre dışı
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw text: {text}")
            # Fallback response
            fallback = get_fallback_response()
            # save_to_cache(cache_key, fallback)  # Cache devre dışı
            return json.dumps(fallback)
            
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback response
        fallback = get_fallback_response()
        # save_to_cache(cache_key, fallback)  # Cache devre dışı
        return json.dumps(fallback)

if __name__ == "__main__":
    result = generate_listening_example()
    print("--- Listening Example ---")
    print(result)

    # Test için JSON parse
    try:
        parsed = json.loads(result)
        print("\nParsed JSON:")
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print("Parsing error:", e) 