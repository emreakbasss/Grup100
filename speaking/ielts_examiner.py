# ielts_examiner.py

import google.generativeai as genai
from config import GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)


class IELTSExaminer:
    """
    Bu sınıf, IELTS Speaking sınavını yöneten yapay zeka görevlisidir.
    Sınav akışını kontrol eder, sorular sorar ve konuşma geçmişini tutar.
    """

    def __init__(self, model_name="gemini-1.5-flash"):
        """
        Examiner'ı başlatır ve Gemini modelini hazırlar.
        """
        self.model = genai.GenerativeModel(model_name)

        # Sınav boyunca tüm konuşmayı (hem bizim prompt'larımız hem de kullanıcının cevapları)
        # saklamak için bir liste oluşturuyoruz. Bu, en sonda geri bildirim için kullanılacak.
        self.conversation_history = []

        # Gemini ile sohbet oturumunu başlatıyoruz. Bu sayede Gemini, konuşmanın bağlamını hatırlar.
        self.chat = self.model.start_chat(history=[])
        print("IELTS Examiner başlatıldı.")

    def ask_question(self, prompt):
        """
        Gemini'ye bir direktif (prompt) gönderir ve modelin cevabını (sorusunu) alır.
        """
        # Gemini'ye prompt'u göndererek bir cevap üretmesini istiyoruz.
        response = self.chat.send_message(prompt)

        # Gemini'nin cevabını (yani kullanıcıya soracağı soruyu) geçmişe kaydediyoruz.
        self.conversation_history.append(f"Examiner's Question: {response.text}")

        return response.text

    def record_user_answer(self, answer):
        """
        Kullanıcının verdiği cevabı konuşma geçmişine kaydeder.
        """
        # Eğer kullanıcı bir cevap verdiyse (None değilse) geçmişe ekle.
        if answer:
            self.conversation_history.append(f"User's Answer: {answer}")

    def generate_final_feedback(self):
        """
        Tüm konuşma geçmişini kullanarak Gemini'den nihai bir değerlendirme ve geri bildirim ister.
        """
        print("\nDeğerlendirme oluşturuluyor... Lütfen bekleyin.")

        # Tüm konuşma geçmişini tek bir metin bloğu haline getiriyoruz.
        full_conversation = "\n".join(self.conversation_history)

        # Geri bildirim istemek için kullanacağımız detaylı prompt.
        feedback_prompt = f"""
        You are an expert IELTS examiner. Your task is to analyze the following conversation transcript from an IELTS Speaking test and provide a detailed evaluation.

        Conversation Transcript:
        ---
        {full_conversation}
        ---

        Please provide a detailed evaluation based on the official IELTS criteria. Structure your feedback as follows:

        **1. Estimated Band Score (1-9):** Provide an overall estimated score.

        **2. Detailed Analysis:**
        * **Fluency and Coherence:** Comment on the candidate's ability to speak at length, the flow of speech, speed, and use of cohesive devices (e.g., 'however', 'in addition', 'for instance'). Note any unnatural pauses or self-corrections.
        * **Lexical Resource (Vocabulary):** Analyze the range and precision of the vocabulary used. Highlight any good idiomatic language or less common words. Also, point out any instances of repetition or simple word choices where a better alternative could have been used.
        * **Grammatical Range and Accuracy:** Assess the variety and correctness of sentence structures. Identify any grammatical errors and explain them clearly.
        * **Pronunciation (from text):** Based on the text provided, note any potential signs of pronunciation issues, such as simple phrasing that might indicate an avoidance of more complex sounds (this is a limitation, but provide what you can infer).

        **3. Actionable Suggestions for Improvement:**
        * Provide specific examples from the user's text.
        * For each mistake identified (e.g., a grammatical error), show the incorrect sentence and then provide the corrected version.
        * Suggest stronger, more impressive vocabulary alternatives for weaker words used by the candidate.
        """


        feedback = self.model.generate_content(feedback_prompt)
        return feedback.text