# app.py
from flask import Flask, render_template, jsonify, request
from listening_generator import generate_listening_example
from google_tts_service import generate_google_tts
import json
import os
import threading
import time
import queue
import traceback

app = Flask(__name__)

# Static folder oluştur
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Cache için gelişmiş sistem
_generated_cache = {}
_cache_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/listening')
def listening():
    return render_template('listening.html')

@app.route('/speaking')
def speaking():
    return render_template('speaking.html')

@app.route('/writing')
def writing():
    return render_template('writing.html')

@app.route('/reading')
def reading():
    return render_template('reading.html')

@app.route('/generate-listening')
def generate_listening():
    try:
        start_time = time.time()
        print(f"=== Starting generation at {start_time} ===")
        
        # Gemini'den listening örneği al
        print("Step 1: Generating AI content...")
        try:
            result = generate_listening_example()
            print(f"AI Response received: {result[:100]}...")
        except Exception as ai_error:
            print(f"AI Error: {ai_error}")
            print(f"AI Error Traceback: {traceback.format_exc()}")
            raise ai_error
        
        # JSON parse et
        print("Step 2: Parsing JSON...")
        try:
            data = json.loads(result)
            print(f"Parsed data keys: {list(data.keys())}")
        except Exception as parse_error:
            print(f"JSON Parse Error: {parse_error}")
            print(f"Raw result: {result}")
            raise parse_error
        
        # Dialogue'u birleştir
        dialogue_text = " ".join(data['dialogue'])
        print(f"Dialogue text: {dialogue_text[:50]}...")
        
        # TTS ile ses dosyası oluştur - async olarak
        print("Step 3: Generating audio...")
        try:
            audio_filename = f"listening_{hash(dialogue_text) % 10000}.mp3"
            audio_path = generate_google_tts(dialogue_text, filename=audio_filename)
            print(f"Audio path: {audio_path}")
        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            print(f"TTS Error Traceback: {traceback.format_exc()}")
            raise tts_error
        
        # Audio URL'ini oluştur
        audio_url = f"/static/audio/{os.path.basename(audio_path)}"
        print(f"Audio URL: {audio_url}")
        
        # Unique dialogue_id oluştur
        dialogue_id = f"dlg_{int(time.time())}_{hash(dialogue_text) % 10000}"
        
        # Response oluştur
        response_data = {
            'dialogue': data['dialogue'],
            'question': data['question'],
            'options': data['options'],
            'answer': data['answer'],
            'audio_url': audio_url,
            'dialogue_id': dialogue_id
        }
        
        # Cache'e kaydet - dialogue_id ile
        _generated_cache[dialogue_id] = response_data
        print(f"Cache saved with dialogue_id: {dialogue_id}")
        print(f"Cache size: {len(_generated_cache)}")
        
        end_time = time.time()
        print(f"=== Total generation time: {end_time - start_time:.2f} seconds ===")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"=== CRITICAL ERROR: {e} ===")
        print(f"=== ERROR TRACEBACK: {traceback.format_exc()} ===")
        
        # Fallback response
        fallback_id = f"dlg_fallback_{int(time.time())}"
        fallback_data = {
            'dialogue': [
                "A: Hi, I'm calling about the job vacancy you advertised.",
                "B: Yes, we're still accepting applications until Friday."
            ],
            'question': "When is the application deadline?",
            'options': {"A": "Monday", "B": "Wednesday", "C": "Friday", "D": "Sunday"},
            'answer': "C",
            'audio_url': "/static/audio/fallback.mp3",
            'dialogue_id': fallback_id
        }
        
        # Fallback'ı da cache'e kaydet
        _generated_cache[fallback_id] = fallback_data
        print("Returning fallback data due to error")
        return jsonify(fallback_data)

@app.route('/check', methods=['POST'])
def check_answer():
    try:
        data = request.get_json()
        dialogue_id = data.get('dialogue_id')
        user_answer = data.get('user_answer')
        
        print(f"Checking answer for dialogue_id: {dialogue_id}")
        print(f"User answer: {user_answer}")
        print(f"Cache keys: {list(_generated_cache.keys())}")
        
        # Cache'den doğru cevabı al
        correct_answer = None
        if dialogue_id in _generated_cache:
            correct_answer = _generated_cache[dialogue_id].get('answer')
            print(f"Found in cache, correct answer: {correct_answer}")
        else:
            print(f"Dialogue ID not found in cache")
            # Cache'de yoksa tüm cache'i kontrol et
            for key, value in _generated_cache.items():
                if value.get('dialogue_id') == dialogue_id:
                    correct_answer = value.get('answer')
                    print(f"Found in cache with key {key}, correct answer: {correct_answer}")
                    break
        
        if correct_answer:
            is_correct = user_answer == correct_answer
            result = {
                'is_correct': is_correct,
                'correct_answer': correct_answer
            }
            print(f"Result: {result}")
            return jsonify(result)
        else:
            print("Correct answer not found")
            return jsonify({
                'is_correct': False,
                'correct_answer': 'Unknown'
            })
            
    except Exception as e:
        print(f"Error checking answer: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({
            'is_correct': False,
            'correct_answer': 'Error'
        })

@app.route('/reveal/<dialogue_id>')
def reveal_answer(dialogue_id):
    try:
        print(f"Revealing answer for dialogue_id: {dialogue_id}")
        print(f"Cache keys: {list(_generated_cache.keys())}")
        
        # Cache'den doğru cevabı al
        correct_answer = None
        if dialogue_id in _generated_cache:
            correct_answer = _generated_cache[dialogue_id].get('answer')
            print(f"Found in cache, correct answer: {correct_answer}")
        else:
            print(f"Dialogue ID not found in cache")
            # Cache'de yoksa tüm cache'i kontrol et
            for key, value in _generated_cache.items():
                if value.get('dialogue_id') == dialogue_id:
                    correct_answer = value.get('answer')
                    print(f"Found in cache with key {key}, correct answer: {correct_answer}")
                    break
        
        if correct_answer:
            result = {
                'correct_answer': correct_answer
            }
            print(f"Result: {result}")
            return jsonify(result)
        else:
            print("Correct answer not found")
            return jsonify({
                'correct_answer': 'Unknown'
            })
            
    except Exception as e:
        print(f"Error revealing answer: {e}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({
            'correct_answer': 'Error'
        })

@app.route('/generate-speaking')
def generate_speaking():
    try:
        # Speaking için örnek sorular
        speaking_topics = [
            "Describe your hometown",
            "Talk about your favorite hobby",
            "Discuss a memorable trip",
            "Describe your dream job",
            "Talk about your family",
            "Describe a place you would like to visit",
            "Talk about your favorite book or movie",
            "Describe a person who has influenced you",
            "Discuss your future plans",
            "Talk about your favorite food"
        ]
        
        import random
        topic = random.choice(speaking_topics)
        
        response_data = {
            'topic': topic,
            'questions': [
                "Can you tell me about this topic?",
                "What makes this important to you?",
                "How has this influenced your life?",
                "What would you change about this?",
                "How do you think this will change in the future?"
            ],
            'tips': [
                "Speak clearly and at a natural pace",
                "Use a variety of vocabulary",
                "Include personal examples",
                "Show enthusiasm and engagement",
                "Use linking words to connect ideas",
                "Practice pronunciation of key words"
            ]
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Speaking generation error: {e}")
        return jsonify({
            'topic': "Describe your hometown",
            'questions': ["Can you tell me about your hometown?"],
            'tips': ["Speak clearly and naturally"]
        })

@app.route('/generate-writing')
def generate_writing():
    try:
        # Writing için çeşitli görevler
        writing_tasks = [
            {
                'type': 'Task 1',
                'title': 'Academic Writing - Graph Description',
                'description': 'The graph below shows the percentage of people who used different types of transport to travel to work in a European city in 2010 and 2020. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.',
                'image_url': '/static/images/graph_sample.png',
                'word_count': '150-200 words',
                'tips': [
                    'Start with an overview of the main trends',
                    'Use specific data from the graph',
                    'Make comparisons between different years',
                    'Use appropriate vocabulary for describing trends'
                ]
            },
            {
                'type': 'Task 2',
                'title': 'Essay Writing - Technology Impact',
                'description': 'Some people believe that technology has made life easier, while others think it has made life more complicated. Discuss both views and give your opinion.',
                'word_count': '250-300 words',
                'tips': [
                    'Present both sides of the argument',
                    'Use examples to support your points',
                    'Give your opinion clearly',
                    'Use linking words to connect ideas'
                ]
            },
            {
                'type': 'Task 2',
                'title': 'Essay Writing - Education vs Sports',
                'description': 'Many people believe that the government should spend more money on education than on sports and entertainment. To what extent do you agree or disagree?',
                'word_count': '250-300 words',
                'tips': [
                    'Clearly state your position',
                    'Provide specific examples',
                    'Consider both sides of the argument',
                    'Use academic vocabulary'
                ]
            },
            {
                'type': 'Task 1',
                'title': 'Academic Writing - Process Description',
                'description': 'The diagram below shows how a solar panel works. Summarize the information by selecting and reporting the main features.',
                'word_count': '150-200 words',
                'tips': [
                    'Describe the process step by step',
                    'Use passive voice where appropriate',
                    'Include all key stages',
                    'Use time connectors'
                ]
            },
            {
                'type': 'Task 2',
                'title': 'Essay Writing - Environmental Issues',
                'description': 'Climate change is one of the biggest challenges facing the world today. What are the main causes of climate change and what solutions can be implemented?',
                'word_count': '250-300 words',
                'tips': [
                    'Identify specific causes and solutions',
                    'Use scientific vocabulary',
                    'Provide concrete examples',
                    'Consider global and local perspectives'
                ]
            },
            {
                'type': 'Task 2',
                'title': 'Essay Writing - Social Media',
                'description': 'Social media has changed the way people communicate. Do you think this change has been positive or negative? Give reasons for your answer.',
                'word_count': '250-300 words',
                'tips': [
                    'Consider both positive and negative aspects',
                    'Use specific examples from social media',
                    'Discuss impact on different age groups',
                    'Consider privacy and mental health issues'
                ]
            },
            {
                'type': 'Task 1',
                'title': 'Academic Writing - Map Comparison',
                'description': 'The maps below show the development of a small town from 1990 to 2020. Summarize the information by selecting and reporting the main features.',
                'word_count': '150-200 words',
                'tips': [
                    'Focus on major changes',
                    'Use directional language',
                    'Compare the two time periods',
                    'Use appropriate prepositions'
                ]
            },
            {
                'type': 'Task 2',
                'title': 'Essay Writing - Work-Life Balance',
                'description': 'In many countries, people are working longer hours and have less free time. What are the causes of this trend and what solutions can be suggested?',
                'word_count': '250-300 words',
                'tips': [
                    'Identify economic and social causes',
                    'Suggest practical solutions',
                    'Consider government and individual roles',
                    'Discuss work-life balance benefits'
                ]
            }
        ]
        
        import random
        task = random.choice(writing_tasks)
        
        response_data = {
            'task': task,
            'criteria': {
                'task_achievement': 'Address all parts of the question and stay within the word limit',
                'coherence_and_cohesion': 'Organize ideas logically with clear paragraph structure and linking words',
                'lexical_resource': 'Use varied and appropriate vocabulary with accurate spelling',
                'grammatical_range_and_accuracy': 'Use different sentence structures with good grammar and punctuation'
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Writing generation error: {e}")
        return jsonify({
            'task': {
                'type': 'Task 2',
                'title': 'Essay Writing',
                'description': 'Discuss the advantages and disadvantages of living in a big city.',
                'word_count': '250-300 words',
                'tips': [
                    'Present both advantages and disadvantages',
                    'Use specific examples',
                    'Give your opinion',
                    'Use appropriate vocabulary'
                ]
            },
            'criteria': {
                'task_achievement': 'Address all parts of the question',
                'coherence_and_cohesion': 'Organize ideas logically',
                'lexical_resource': 'Use varied vocabulary',
                'grammatical_range_and_accuracy': 'Use different sentence structures'
            }
        })

@app.route('/check-writing', methods=['POST'])
def check_writing():
    try:
        print("=== Writing Check Request ===")
        
        # Request data kontrolü
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({
                'error': 'Invalid request format. Expected JSON.'
            }), 400
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        user_text = data.get('text', '')
        print(f"User text length: {len(user_text)}")
        
        if not user_text.strip():
            print("Error: No text provided")
            return jsonify({
                'error': 'No text provided for checking'
            }), 400
        
        # Basit yazı denetleme (gerçek bir AI servisi kullanılabilir)
        print("Starting writing analysis...")
        feedback = analyze_writing(user_text)
        print(f"Analysis completed. Score: {feedback.get('overall_score', 0)}")
        
        return jsonify(feedback)
        
    except Exception as e:
        print(f"=== CRITICAL WRITING CHECK ERROR ===")
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Error checking writing',
            'details': str(e),
            'type': str(type(e))
        }), 500

@app.route('/analyze-speaking', methods=['POST'])
def analyze_speaking():
    try:
        data = request.get_json()
        transcript = data.get('transcript', '')
        
        if not transcript.strip():
            return jsonify({'error': 'No transcript provided'}), 400
        
        analysis = analyze_speaking_transcript(transcript)
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_speaking_transcript(transcript):
    """Gelişmiş IELTS speaking analizi - Profesyonel seviye"""
    analysis = {
        'overall_score': 0,
        'word_count': 0,
        'speaking_errors': [],
        'fluency_score': 0,
        'pronunciation_score': 0,
        'grammar_score': 0,
        'vocabulary_score': 0,
        'suggestions': [],
        'strengths': [],
        'band_score': {
            'fluency_coherence': 0,
            'lexical_resource': 0,
            'grammatical_range': 0,
            'pronunciation': 0
        },
        'detailed_analysis': {
            'fluency_issues': [],
            'pronunciation_issues': [],
            'grammar_issues': [],
            'vocabulary_usage': [],
            'coherence_issues': []
        }
    }
    
    # Kelime sayısı analizi
    words = transcript.strip().split()
    meaningful_words = [word for word in words if len(word) > 2 and word.isalpha()]
    analysis['word_count'] = len(meaningful_words)
    
    # Akıcılık analizi
    sentences = transcript.split('.')
    sentence_count = len([s for s in sentences if s.strip()])
    avg_sentence_length = len(meaningful_words) / max(sentence_count, 1)
    
    if avg_sentence_length < 5:
        analysis['detailed_analysis']['fluency_issues'].append("Very short sentences - try to speak in longer, more complex sentences")
        analysis['fluency_score'] = max(0, analysis['fluency_score'] - 20)
    elif avg_sentence_length > 15:
        analysis['detailed_analysis']['fluency_issues'].append("Very long sentences - consider breaking them into shorter, clearer sentences")
        analysis['fluency_score'] = max(0, analysis['fluency_score'] - 10)
    else:
        analysis['fluency_score'] += 30
        analysis['strengths'].append("Good sentence length for speaking")
    
    # Dilbilgisi analizi
    grammar_errors = []
    common_speaking_errors = [
        ('i think', 'I think'),
        ('i dont', 'I don\'t'),
        ('its', 'it\'s'),
        ('i ', 'I '),
        (' i ', ' I '),
        (' dont ', " don't "),
        (' cant ', " can't "),
        (' wont ', " won't "),
        (' isnt ', " isn't "),
        (' arent ', " aren't "),
        (' havent ', " haven't "),
        (' hasnt ', " hasn't "),
        (' wouldnt ', " wouldn't "),
        (' couldnt ', " couldn't "),
        (' shouldnt ', " shouldn't "),
        (' didnt ', " didn't "),
        (' wasnt ', " wasn't "),
        (' werent ', " weren't ")
    ]
    
    for error, correction in common_speaking_errors:
        if error in transcript.lower():
            grammar_errors.append(f"'{error.strip()}' should be '{correction.strip()}'")
    
    analysis['speaking_errors'] = grammar_errors
    analysis['grammar_score'] = max(0, 100 - len(grammar_errors) * 10)
    
    if len(grammar_errors) == 0:
        analysis['strengths'].append("Excellent grammar usage!")
    else:
        analysis['detailed_analysis']['grammar_issues'] = grammar_errors
    
    # Kelime hazinesi analizi
    unique_words = len(set([word.lower() for word in meaningful_words]))
    vocabulary_diversity = unique_words / max(len(meaningful_words), 1)
    
    if vocabulary_diversity > 0.7:
        analysis['vocabulary_score'] += 40
        analysis['strengths'].append("Excellent vocabulary diversity!")
    elif vocabulary_diversity < 0.3:
        analysis['vocabulary_score'] -= 20
        analysis['detailed_analysis']['vocabulary_usage'].append("Limited vocabulary - try using more varied words")
    else:
        analysis['vocabulary_score'] += 20
    
    # Telaffuz analizi (basit)
    pronunciation_indicators = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'sort of', 'kind of']
    filler_count = sum(1 for filler in pronunciation_indicators if filler in transcript.lower())
    
    if filler_count > 5:
        analysis['pronunciation_score'] -= 20
        analysis['detailed_analysis']['pronunciation_issues'].append(f"Too many filler words ({filler_count}) - try to speak more confidently")
    elif filler_count == 0:
        analysis['pronunciation_score'] += 20
        analysis['strengths'].append("Great speaking confidence - no filler words!")
    else:
        analysis['pronunciation_score'] += 10
    
    # Genel skor hesaplama
    analysis['overall_score'] = (
        analysis['fluency_score'] + 
        analysis['grammar_score'] + 
        analysis['vocabulary_score'] + 
        analysis['pronunciation_score']
    ) // 4
    
    # Band skor hesaplama
    analysis['band_score'] = {
        'fluency_coherence': min(9, max(1, (analysis['overall_score'] + 10) // 10)),
        'lexical_resource': min(9, max(1, (analysis['overall_score'] + 5) // 10)),
        'grammatical_range': min(9, max(1, analysis['overall_score'] // 10)),
        'pronunciation': min(9, max(1, (analysis['overall_score'] + 8) // 10))
    }
    
    # Öneriler
    if analysis['word_count'] < 20:
        analysis['suggestions'].append("Try to speak more - aim for at least 50-100 words")
    
    if analysis['fluency_score'] < 50:
        analysis['suggestions'].append("Practice speaking in longer, more connected sentences")
    
    if analysis['grammar_score'] < 70:
        analysis['suggestions'].append("Focus on basic grammar - especially subject-verb agreement")
    
    if analysis['vocabulary_score'] < 60:
        analysis['suggestions'].append("Try to use more varied vocabulary")
    
    if analysis['pronunciation_score'] < 60:
        analysis['suggestions'].append("Work on speaking confidence and reducing filler words")
    
    return analysis

def analyze_writing(text):
    """Gelişmiş IELTS writing analizi - Profesyonel seviye"""
    feedback = {
        'overall_score': 0,
        'word_count': 0,
        'grammar_errors': [],
        'spelling_errors': [],
        'suggestions': [],
        'strengths': [],
        'criteria_feedback': {},
        'detailed_analysis': {
            'sentence_structure': [],
            'vocabulary_usage': [],
            'coherence_issues': [],
            'task_response': [],
            'paragraph_structure': [],
            'academic_style': [],
            'argument_strength': [],
            'evidence_usage': []
        },
        'band_score': {
            'task_achievement': 0,
            'coherence_cohesion': 0,
            'lexical_resource': 0,
            'grammatical_accuracy': 0
        }
    }
    
    # Gelişmiş kelime analizi
    words = text.strip().split()
    meaningful_words = [word for word in words if len(word) > 2 and word.isalpha() and word.lower() not in [
        'the', 'and', 'for', 'but', 'are', 'was', 'were', 'has', 'had', 'will', 'can', 'may', 'must', 'should', 'would', 'could', 'might',
        'this', 'that', 'with', 'from', 'they', 'them', 'their', 'have', 'been', 'being', 'said', 'each', 'which', 'there', 'other', 'about',
        'many', 'then', 'them', 'these', 'people', 'some', 'time', 'very', 'into', 'just', 'only', 'know', 'take', 'than', 'more', 'first',
        'water', 'call', 'who', 'sit', 'now', 'find', 'down', 'day', 'did', 'get', 'come', 'made', 'part', 'over', 'new', 'sound', 'little',
        'work', 'place', 'year', 'live', 'back', 'give', 'most', 'after', 'thing', 'our', 'name', 'good', 'sentence', 'man', 'think', 'say',
        'great', 'where', 'help', 'through', 'much', 'before', 'line', 'right', 'too', 'mean', 'old', 'any', 'same', 'tell', 'boy', 'follow',
        'came', 'want', 'show', 'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end', 'does', 'another', 'well', 'large', 'big',
        'even', 'such', 'because', 'turn', 'here', 'why', 'ask', 'went', 'men', 'read', 'need', 'land', 'different', 'home', 'us', 'move',
        'try', 'kind', 'hand', 'picture', 'again', 'change', 'off', 'play', 'spell', 'air', 'away', 'animal', 'house', 'point', 'page', 'letter',
        'mother', 'answer', 'found', 'study', 'still', 'learn', 'world', 'high', 'every', 'near', 'add', 'food', 'between', 'own', 'below',
        'country', 'plant', 'last', 'school', 'father', 'keep', 'tree', 'never', 'start', 'city', 'earth', 'eye', 'light', 'thought', 'head',
        'under', 'story', 'saw', 'left', 'don\'t', 'few', 'while', 'along', 'close', 'something', 'seem', 'next', 'hard', 'open', 'example',
        'begin', 'life', 'always', 'those', 'both', 'paper', 'together', 'got', 'group', 'often', 'run', 'important', 'until', 'children',
        'side', 'feet', 'car', 'miles', 'night', 'walk', 'white', 'sea', 'began', 'grow', 'took', 'river', 'four', 'carry', 'state', 'once',
        'book', 'hear', 'stop', 'without', 'second', 'late', 'miss', 'idea', 'enough', 'eat', 'face', 'watch', 'far', 'really', 'almost', 'let',
        'above', 'girl', 'sometimes', 'mountain', 'cut', 'young', 'talk', 'soon', 'list', 'song', 'being', 'leave', 'family', 'it\'s'
    ]]
    feedback['word_count'] = len(meaningful_words)
    
    # Gelişmiş dilbilgisi ve yazım kontrolü
    common_errors = [
        ('i think', 'I think'),
        ('i dont', 'I don\'t'),
        ('its', 'it\'s'),
        ('definately', 'definitely'),
        ('recieve', 'receive'),
        ('occured', 'occurred'),
        ('begining', 'beginning'),
        ('beleive', 'believe'),
        ('seperate', 'separate'),
        ('accomodate', 'accommodate'),
        ('neccessary', 'necessary'),
        ('occassion', 'occasion'),
        ('sucess', 'success'),
        ('enviroment', 'environment'),
        ('goverment', 'government'),
        ('sociaty', 'society'),
        ('technolgy', 'technology'),
        ('importent', 'important'),
        ('diffrent', 'different'),
        ('probablly', 'probably'),
        ('i ', 'I '),
        (' i ', ' I '),
        (' dont ', " don't "),
        (' cant ', " can't "),
        (' wont ', " won't "),
        (' isnt ', " isn't "),
        (' arent ', " aren't "),
        (' havent ', " haven't "),
        (' hasnt ', " hasn't "),
        (' wouldnt ', " wouldn't "),
        (' couldnt ', " couldn't "),
        (' shouldnt ', " shouldn't "),
        (' didnt ', " didn't "),
        (' wasnt ', " wasn't "),
        (' werent ', " weren't ")
    ]
    
    corrected_text = text
    for error, correction in common_errors:
        if error in text.lower():
            feedback['grammar_errors'].append(f"'{error.strip()}' should be '{correction.strip()}'")
            corrected_text = corrected_text.replace(error, correction)
    
    # Gelişmiş yazım kontrolü
    common_misspellings = [
        ('recieve', 'receive'), ('seperate', 'separate'), ('definately', 'definitely'),
        ('occassion', 'occasion'), ('accomodate', 'accommodate'), ('begining', 'beginning'),
        ('beleive', 'believe'), ('bussiness', 'business'), ('calender', 'calendar'),
        ('collegue', 'colleague'), ('concious', 'conscious'), ('embarass', 'embarrass'),
        ('enviroment', 'environment'), ('foward', 'forward'), ('freind', 'friend'),
        ('futher', 'further'), ('goverment', 'government'), ('grammer', 'grammar'),
        ('happend', 'happened'), ('immediatly', 'immediately'), ('independant', 'independent'),
        ('knowlege', 'knowledge'), ('lenght', 'length'), ('liase', 'liaise'),
        ('liason', 'liaison'), ('maintainance', 'maintenance'), ('neccessary', 'necessary'),
        ('occassionally', 'occasionally'), ('occured', 'occurred'), ('occurence', 'occurrence'),
        ('oppurtunity', 'opportunity'), ('paralell', 'parallel'), ('peice', 'piece'),
        ('percieve', 'perceive'), ('posession', 'possession'), ('prefered', 'preferred'),
        ('priviledge', 'privilege'), ('probaly', 'probably'), ('proffesional', 'professional'),
        ('promiss', 'promise'), ('pronounciation', 'pronunciation'), ('prupose', 'purpose'),
        ('quater', 'quarter'), ('questionaire', 'questionnaire'), ('reccomend', 'recommend'),
        ('rediculous', 'ridiculous'), ('refered', 'referred'), ('refering', 'referring'),
        ('religous', 'religious'), ('rember', 'remember'), ('remenber', 'remember'),
        ('resistence', 'resistance'), ('resourse', 'resource'), ('responce', 'response'),
        ('responsable', 'responsible'), ('sence', 'since'), ('sincerly', 'sincerely'),
        ('sucess', 'success'), ('sucessful', 'successful'), ('sucessfully', 'successfully'),
        ('suprise', 'surprise'), ('suprised', 'surprised'), ('tendancy', 'tendency'),
        ('therefor', 'therefore'), ('threshhold', 'threshold'), ('tommorow', 'tomorrow'),
        ('tounge', 'tongue'), ('truely', 'truly'), ('unfortunatly', 'unfortunately'),
        ('untill', 'until'), ('wierd', 'weird'), ('whereever', 'wherever'),
        ('wich', 'which'), ('wonderfull', 'wonderful'), ('writting', 'writing'),
        ('writen', 'written')
    ]
    
    for misspelling, correction in common_misspellings:
        if misspelling in text.lower():
            feedback['spelling_errors'].append(f"'{misspelling}' should be '{correction}'")

    # Gelişmiş cümle yapısı analizi
    sentences = text.split('.')
    sentence_count = len([s for s in sentences if s.strip()])

    # Cümle uzunluğu analizi
    long_sentences = 0
    short_sentences = 0
    sentence_details = []
    
    for i, sentence in enumerate(sentences, 1):
        if sentence.strip():
            word_count = len(sentence.strip().split())
            sentence_text = sentence.strip()
            
            if word_count > 25:
                long_sentences += 1
                # Cümleyi kısaltmak için öneriler
                suggestions = []
                if word_count > 50:
                    suggestions.append("Break into 2-3 shorter sentences")
                elif word_count > 35:
                    suggestions.append("Consider using semicolons or conjunctions")
                
                feedback['detailed_analysis']['sentence_structure'].append(
                    f"Sentence #{i}: {sentence_text[:50]}{'...' if len(sentence_text) > 50 else ''} "
                    f"({word_count} words) - {'; '.join(suggestions)}"
                )
            elif word_count < 5:
                short_sentences += 1
                feedback['detailed_analysis']['sentence_structure'].append(
                    f"Sentence #{i}: '{sentence_text}' ({word_count} words) - Consider adding more detail"
                )
            elif word_count >= 15 and word_count <= 25:
                # İyi uzunluktaki cümleleri öv
                feedback['detailed_analysis']['sentence_structure'].append(
                    f"Sentence #{i}: Good length ({word_count} words) - Well-structured"
                )
    
    # Paragraf yapısı analizi
    paragraphs = text.split('\n\n')
    if len(paragraphs) < 2 and len(meaningful_words) > 100:
        feedback['detailed_analysis']['paragraph_structure'].append("Consider dividing your essay into clear paragraphs")
    
    # Akademik kelime kullanımı analizi
    academic_words = ['furthermore', 'moreover', 'nevertheless', 'consequently', 'therefore', 'however', 'nevertheless', 
                     'subsequently', 'additionally', 'similarly', 'conversely', 'nevertheless', 'meanwhile', 'accordingly']
    used_academic_words = [word for word in academic_words if word.lower() in text.lower()]
    
    if len(used_academic_words) == 0 and len(meaningful_words) > 50:
        feedback['detailed_analysis']['vocabulary_usage'].append("Consider using more academic linking words")
    elif len(used_academic_words) >= 3:
        feedback['detailed_analysis']['vocabulary_usage'].append(f"Good use of academic vocabulary: {', '.join(used_academic_words)}")
    
    # Argüman gücü analizi
    argument_indicators = ['because', 'since', 'as', 'therefore', 'thus', 'hence', 'consequently', 'as a result']
    argument_count = sum(1 for indicator in argument_indicators if indicator in text.lower())
    
    if argument_count == 0 and len(meaningful_words) > 50:
        feedback['detailed_analysis']['argument_strength'].append("Consider adding more logical connections and reasoning")
    elif argument_count >= 3:
        feedback['detailed_analysis']['argument_strength'].append("Good use of logical connections and reasoning")
    
    # Kanıt kullanımı analizi
    evidence_indicators = ['for example', 'such as', 'specifically', 'in particular', 'for instance', 'e.g.', 'i.e.']
    evidence_count = sum(1 for indicator in evidence_indicators if indicator in text.lower())
    
    if evidence_count == 0 and len(meaningful_words) > 100:
        feedback['detailed_analysis']['evidence_usage'].append("Consider adding specific examples to support your arguments")
    elif evidence_count >= 2:
        feedback['detailed_analysis']['evidence_usage'].append("Good use of examples and evidence")
    
    # Gelişmiş öneriler
    meaningful_text = len(meaningful_words)
    
    if len(meaningful_words) < 100:
        feedback['suggestions'].append("Your essay is too short. Aim for at least 150-200 meaningful words for Task 1 and 250-300 words for Task 2.")
    elif len(meaningful_words) > 350:
        feedback['suggestions'].append("Your essay is quite long. Try to be more concise while maintaining quality.")
    
    if long_sentences > 2:
        feedback['suggestions'].append("You have several very long sentences. Consider breaking them into shorter, clearer sentences.")
    
    if short_sentences > 3:
        feedback['suggestions'].append("You have many short sentences. Try combining some to create more complex structures.")
    
    if not any(word in text.lower() for word in ['firstly', 'secondly', 'finally', 'moreover', 'furthermore', 'however', 'nevertheless', 'therefore', 'consequently']):
        feedback['suggestions'].append("Consider using more linking words to improve coherence.")
    
    if text.count('.') < 3:
        feedback['suggestions'].append("Try to write more complex sentences with proper punctuation.")
    
    # Gelişmiş güçlü yanlar
    if len(feedback['grammar_errors']) == 0 and meaningful_text > 10:
        feedback['strengths'].append("Excellent grammar usage!")
    
    if len(feedback['spelling_errors']) == 0 and meaningful_text > 10:
        feedback['strengths'].append("Perfect spelling!")
    
    if len(meaningful_words) >= 150 and meaningful_text > 50:
        feedback['strengths'].append("Good word count for the task.")
    
    if len(used_academic_words) >= 3:
        feedback['strengths'].append("Strong academic vocabulary usage.")
    
    if argument_count >= 3:
        feedback['strengths'].append("Good logical reasoning and argument structure.")
    
    if evidence_count >= 2:
        feedback['strengths'].append("Effective use of examples and evidence.")
    
    # Anlamsız yazılar için uyarı
    if meaningful_text < 5:
        feedback['suggestions'].append("Please write a meaningful response with proper sentences.")
        feedback['strengths'] = []
    
    # Gelişmiş skor hesaplama
    score = 100
    
    # Dilbilgisi ve yazım puanı
    score -= len(feedback['grammar_errors']) * 3
    score -= len(feedback['spelling_errors']) * 2
    
    # Cümle yapısı puanı
    score -= long_sentences * 2
    score -= short_sentences * 1
    
    # Akademik kelime puanı
    if len(used_academic_words) >= 3:
        score += 10
    elif len(used_academic_words) == 0:
        score -= 5
    
    # Argüman gücü puanı
    if argument_count >= 3:
        score += 8
    elif argument_count == 0:
        score -= 5
    
    # Kanıt kullanımı puanı
    if evidence_count >= 2:
        score += 7
    elif evidence_count == 0:
        score -= 3
    
    # Anlamsız yazılar için ekstra düşürme
    if meaningful_text < 5:
        score = max(0, score - 80)
    elif meaningful_text < 10:
        score = max(0, score - 40)
    
    score = max(0, min(100, score))
    feedback['overall_score'] = score
    
    # Gelişmiş band skor hesaplama
    feedback['band_score'] = {
        'task_achievement': min(9, max(1, (score + 5) // 10)),
        'coherence_cohesion': min(9, max(1, (score + 8) // 10)),
        'lexical_resource': min(9, max(1, (score + 3) // 10)),
        'grammatical_accuracy': min(9, max(1, score // 10))
    }
    
    # Teknik analiz istatistikleri
    feedback['technical_stats'] = {
        'total_sentences': sentence_count,
        'long_sentences': long_sentences,
        'short_sentences': short_sentences,
        'academic_words_used': len(used_academic_words),
        'argument_indicators': argument_count,
        'evidence_indicators': evidence_count,
        'paragraphs': len(paragraphs),
        'avg_sentence_length': round(len(meaningful_words) / max(1, sentence_count), 1),
        'complexity_score': min(100, (len(used_academic_words) * 10 + argument_count * 8 + evidence_count * 7))
    }
    
    # Gelişmiş kriter bazlı geri bildirim
    feedback['criteria_feedback'] = {
        'task_achievement': {
            'score': feedback['band_score']['task_achievement'],
            'comment': 'Excellent task response with clear addressing of all parts' if score > 80 else 
                      'Good task response' if score > 60 else 'Needs improvement in addressing the task'
        },
        'coherence_and_cohesion': {
            'score': feedback['band_score']['coherence_cohesion'],
            'comment': 'Well-organized ideas with excellent paragraph structure' if score > 80 else 
                      'Well-organized ideas' if score > 60 else 'Consider better paragraph structure and linking'
        },
        'lexical_resource': {
            'score': feedback['band_score']['lexical_resource'],
            'comment': 'Excellent vocabulary range with academic words' if score > 80 else 
                      'Good vocabulary range' if score > 60 else 'Try using more varied and academic vocabulary'
        },
        'grammatical_range_and_accuracy': {
            'score': feedback['band_score']['grammatical_accuracy'],
            'comment': 'Excellent grammar with varied sentence structures' if score > 80 else 
                      'Good grammar usage' if score > 60 else 'Focus on grammar accuracy and sentence variety'
        }
    }
    
    return feedback

@app.route('/generate-reading')
def generate_reading():
    try:
        # Reading için çeşitli konular
        reading_topics = [
            {
                'title': 'The Future of Artificial Intelligence',
                'topic': 'technology and AI',
                'text': 'Artificial Intelligence (AI) has rapidly evolved from a concept in science fiction to a transformative technology that is reshaping industries worldwide. Machine learning algorithms, neural networks, and deep learning systems are now capable of performing tasks that were once thought to be exclusively human, from recognizing patterns in medical images to predicting consumer behavior with remarkable accuracy. However, this rapid advancement has also raised important questions about job displacement, ethical considerations, and the need for responsible AI development. As AI systems become more sophisticated, researchers and policymakers are working to establish frameworks that ensure these technologies benefit society while minimizing potential risks.',
                'questions': [
                    {
                        'question': 'What is the main focus of the passage?',
                        'options': ['The history of AI development', 'The current state and future of AI', 'The risks of AI technology', 'The ethical concerns of AI'],
                        'answer': 1
                    },
                    {
                        'question': 'According to the passage, what can AI systems now do?',
                        'options': ['Only basic calculations', 'Recognize medical patterns and predict behavior', 'Replace all human jobs', 'Solve all ethical problems'],
                        'answer': 1
                    },
                    {
                        'question': 'What concern is mentioned in the passage?',
                        'options': ['AI is too expensive', 'Job displacement and ethical considerations', 'AI is not advanced enough', 'AI is only used in medicine'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'Climate Change and Global Sustainability',
                'topic': 'environment and climate',
                'text': 'Climate change represents one of the most pressing challenges of our time, with far-reaching implications for ecosystems, economies, and human societies. The scientific consensus is clear: human activities, particularly the burning of fossil fuels and deforestation, have significantly contributed to rising global temperatures. This warming has led to more frequent and intense extreme weather events, rising sea levels, and shifts in precipitation patterns. However, there is also growing evidence that concerted global action can mitigate these effects. Renewable energy technologies, sustainable agricultural practices, and international cooperation offer pathways toward a more sustainable future. The transition to a low-carbon economy, while challenging, presents opportunities for innovation and job creation in emerging green industries.',
                'questions': [
                    {
                        'question': 'What is the main cause of climate change according to the passage?',
                        'options': ['Natural phenomena only', 'Human activities like burning fossil fuels', 'Solar radiation', 'Volcanic eruptions'],
                        'answer': 1
                    },
                    {
                        'question': 'What are the effects of climate change mentioned?',
                        'options': ['Only temperature rise', 'Extreme weather, sea level rise, and precipitation changes', 'Only economic impacts', 'Only environmental impacts'],
                        'answer': 1
                    },
                    {
                        'question': 'What solutions are mentioned in the passage?',
                        'options': ['Only renewable energy', 'Renewable energy, sustainable agriculture, and international cooperation', 'Only government action', 'Only individual action'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'The Psychology of Learning and Memory',
                'topic': 'psychology and education',
                'text': 'Understanding how humans learn and retain information has been a central focus of psychological research for over a century. Modern neuroscience has revealed that learning is not a passive process but an active construction of knowledge that involves multiple brain regions working together. Memory formation, consolidation, and retrieval are complex processes influenced by factors such as attention, emotional state, and prior knowledge. Research has shown that active learning strategies, such as spaced repetition and elaborative encoding, significantly improve retention compared to passive reading or rote memorization. Furthermore, the role of sleep in memory consolidation has become increasingly clear, with studies demonstrating that adequate sleep is crucial for optimal learning outcomes.',
                'questions': [
                    {
                        'question': 'What does modern neuroscience reveal about learning?',
                        'options': ['It is a passive process', 'It is an active construction involving multiple brain regions', 'It only involves one part of the brain', 'It is not related to memory'],
                        'answer': 1
                    },
                    {
                        'question': 'What factors influence memory formation?',
                        'options': ['Only attention', 'Attention, emotional state, and prior knowledge', 'Only sleep', 'Only repetition'],
                        'answer': 1
                    },
                    {
                        'question': 'What is the role of sleep in learning?',
                        'options': ['It has no effect', 'It is crucial for memory consolidation', 'It only affects physical health', 'It only affects attention'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'The Evolution of Digital Communication',
                'topic': 'technology and communication',
                'text': 'The landscape of human communication has undergone a dramatic transformation in the digital age. From the early days of email and instant messaging to the current era of social media platforms and video conferencing, digital technologies have fundamentally altered how we connect, collaborate, and share information. This evolution has brought both opportunities and challenges. On the positive side, digital communication has enabled global connectivity, facilitated remote work, and democratized access to information. However, it has also raised concerns about privacy, digital addiction, and the quality of interpersonal relationships. The rapid pace of technological change continues to shape communication patterns, with emerging technologies like virtual reality and artificial intelligence poised to further transform how we interact.',
                'questions': [
                    {
                        'question': 'What has digital technology done to human communication?',
                        'options': ['Made it worse', 'Fundamentally altered how we connect and share information', 'Had no effect', 'Only affected business communication'],
                        'answer': 1
                    },
                    {
                        'question': 'What are the positive effects mentioned?',
                        'options': ['Only global connectivity', 'Global connectivity, remote work, and democratized information access', 'Only privacy concerns', 'Only digital addiction'],
                        'answer': 1
                    },
                    {
                        'question': 'What concerns are raised about digital communication?',
                        'options': ['Only cost', 'Privacy, digital addiction, and relationship quality', 'Only technical issues', 'Only accessibility'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'The Science of Nutrition and Health',
                'topic': 'health and nutrition',
                'text': 'Nutrition science has evolved significantly over the past few decades, moving beyond simple calorie counting to a more nuanced understanding of how different foods affect our bodies at the molecular level. Research has revealed that the relationship between diet and health is complex, influenced by factors such as genetics, gut microbiome, and individual metabolic responses. The concept of personalized nutrition has emerged, recognizing that there is no one-size-fits-all approach to healthy eating. Studies have shown that whole foods, rich in fiber and nutrients, generally provide better health outcomes than highly processed alternatives. Furthermore, the timing of meals and the composition of our gut bacteria play crucial roles in how our bodies process and utilize nutrients.',
                'questions': [
                    {
                        'question': 'How has nutrition science evolved?',
                        'options': ['It has become simpler', 'It has moved from calorie counting to molecular-level understanding', 'It has focused only on weight loss', 'It has ignored individual differences'],
                        'answer': 1
                    },
                    {
                        'question': 'What factors influence the diet-health relationship?',
                        'options': ['Only calories', 'Genetics, gut microbiome, and metabolic responses', 'Only exercise', 'Only age'],
                        'answer': 1
                    },
                    {
                        'question': 'What is personalized nutrition?',
                        'options': ['Eating the same foods as everyone else', 'Recognizing that there is no one-size-fits-all approach', 'Only eating organic food', 'Only counting calories'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'Urban Planning and Sustainable Cities',
                'topic': 'urban development and sustainability',
                'text': 'As the world becomes increasingly urbanized, the importance of thoughtful urban planning has never been greater. Modern cities face complex challenges including traffic congestion, air pollution, housing affordability, and climate resilience. Sustainable urban development requires a holistic approach that considers environmental, social, and economic factors. Green infrastructure, such as urban parks, green roofs, and permeable surfaces, can help cities adapt to climate change while improving quality of life. Public transportation systems, when well-designed and integrated, can reduce car dependency and associated emissions. The concept of the 15-minute city, where essential services are accessible within a short walk or bike ride, represents a promising model for creating more livable and sustainable urban environments.',
                'questions': [
                    {
                        'question': 'What challenges do modern cities face?',
                        'options': ['Only traffic', 'Traffic congestion, air pollution, housing affordability, and climate resilience', 'Only housing', 'Only pollution'],
                        'answer': 1
                    },
                    {
                        'question': 'What is green infrastructure?',
                        'options': ['Only parks', 'Urban parks, green roofs, and permeable surfaces', 'Only buildings', 'Only roads'],
                        'answer': 1
                    },
                    {
                        'question': 'What is the 15-minute city concept?',
                        'options': ['A city with 15-minute traffic lights', 'Where essential services are accessible within a short walk or bike ride', 'A city that takes 15 minutes to cross', 'A city with 15-minute work days'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'The Psychology of Decision Making',
                'topic': 'psychology and behavior',
                'text': 'Human decision-making is a fascinating area of study that combines insights from psychology, neuroscience, and behavioral economics. Research has revealed that our decisions are often influenced by cognitive biases, emotional states, and social factors rather than pure rational analysis. The availability heuristic, for example, leads us to overestimate the probability of events that are easily recalled, while the anchoring effect causes us to rely too heavily on the first piece of information we receive. Understanding these biases can help individuals make better decisions and organizations design more effective policies. However, it is important to note that some biases may have evolved as adaptive responses to complex environments, even if they sometimes lead to suboptimal choices in modern contexts.',
                'questions': [
                    {
                        'question': 'What influences human decision-making?',
                        'options': ['Only logic', 'Cognitive biases, emotional states, and social factors', 'Only education', 'Only experience'],
                        'answer': 1
                    },
                    {
                        'question': 'What is the availability heuristic?',
                        'options': ['Making decisions based on availability of time', 'Overestimating probability of easily recalled events', 'Always choosing the first option', 'Making decisions based on cost'],
                        'answer': 1
                    },
                    {
                        'question': 'Why is understanding biases important?',
                        'options': ['To avoid all decisions', 'To make better decisions and design effective policies', 'To eliminate all biases', 'To ignore emotions'],
                        'answer': 1
                    }
                ]
            },
            {
                'title': 'The Future of Renewable Energy',
                'topic': 'energy and sustainability',
                'text': 'The transition to renewable energy sources represents one of the most significant technological and economic shifts of the 21st century. Solar and wind power have become increasingly cost-competitive with fossil fuels, driven by technological advances and economies of scale. Energy storage technologies, particularly battery systems, are crucial for addressing the intermittent nature of renewable sources and enabling their widespread adoption. The development of smart grids, which can dynamically balance supply and demand, is essential for integrating renewable energy into existing infrastructure. While challenges remain, including the need for investment in transmission infrastructure and the development of new energy storage solutions, the economic and environmental benefits of renewable energy make it a compelling path forward.',
                'questions': [
                    {
                        'question': 'What has made renewable energy more competitive?',
                        'options': ['Only government subsidies', 'Technological advances and economies of scale', 'Only environmental concerns', 'Only public demand'],
                        'answer': 1
                    },
                    {
                        'question': 'Why is energy storage important?',
                        'options': ['To reduce costs', 'To address the intermittent nature of renewable sources', 'To increase pollution', 'To reduce efficiency'],
                        'answer': 1
                    },
                    {
                        'question': 'What is a smart grid?',
                        'options': ['A grid that is always on', 'A grid that can dynamically balance supply and demand', 'A grid that only uses solar power', 'A grid that is cheaper'],
                        'answer': 1
                    }
                ]
            }
        ]
        
        import random
        selected_topic = random.choice(reading_topics)
        
        response_data = {
            'passage': selected_topic,
            'time_limit': '20 minutes',
            'tips': [
                'Read the questions first to understand what to look for',
                'Skim the passage to get the main idea before reading in detail',
                'Look for keywords from the questions in the passage',
                'Pay attention to topic sentences and concluding paragraphs',
                'Use the process of elimination for multiple choice questions',
                'Don\'t spend too much time on any single question',
                'Check your answers if time permits'
            ]
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Reading generation error: {e}")
        return jsonify({
            'passage': {
                'title': 'Sample Reading Passage',
                'text': 'This is a sample reading passage for IELTS practice. It contains information about various topics that are commonly found in academic texts.',
                'questions': [
                    {
                        'question': 'What is this passage about?',
                        'options': ['Sample text', 'IELTS practice', 'Reading skills', 'All of the above'],
                        'answer': 3
                    }
                ]
            },
            'time_limit': '20 minutes',
            'tips': ['Read carefully and answer all questions']
        })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'cache_size': len(_generated_cache)})

@app.route('/test')
def test_route():
    return jsonify({'message': 'Server is working!', 'timestamp': time.time()})

@app.route('/clear-cache')
def clear_cache():
    global _generated_cache
    _generated_cache.clear()
    return jsonify({'message': 'Cache cleared!', 'cache_size': 0})

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Optimizations enabled:")
    print("- Caching system active")
    print("- Fast TTS generation")
    print("- Reduced API calls")
    print("- Enhanced error logging")
    print("- New content generation on each request")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True) 