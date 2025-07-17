# main.py
import warnings
warnings.filterwarnings("ignore", message=r"urllib3 v2 only supports OpenSSL 1.1.1\+, currently the 'ssl' module is compiled with.*")


from ielts_examiner import IELTSExaminer
from speech_services import speak_text, listen_to_user
import time


def run_speaking_test():
    """
    IELTS Speaking testini baştan sona yürüten ana fonksiyon.
    """


    examiner = IELTSExaminer()


    speak_text(
        "Hello, welcome to the IELTS Speaking practice test. My name is Gemini, and I will be your examiner today. We will now begin with Part 1.")

    # --- PART 1: Tanışma ve Genel Sorular ---
    # Gemini'ye Part 1'i başlatması için ilk direktifi veriyoruz.
    part1_prompt = "You are an IELTS examiner. Start Part 1 of the test. First, ask for my name. Then, ask me 3-4 questions about the topic 'work or studies'."
    question = examiner.ask_question(part1_prompt)
    speak_text(question)

    # Part 1 için yaklaşık 4 soru-cevap döngüsü yapalım
    for i in range(4):
        user_answer = listen_to_user()
        examiner.record_user_answer(user_answer)

        # Eğer kullanıcı cevap veremediyse döngüyü atla
        if user_answer is None:
            continue

        # Son soruya geldiyse yeni soru isteme
        if i < 3:
            next_prompt = "That's interesting. Please ask the next question on the same topic."
            question = examiner.ask_question(next_prompt)
            speak_text(question)

    # --- PART 2: Uzun Konuşma (Cue Card) ---
    speak_text("Thank you. That is the end of Part 1. We will now move to Part 2.")
    time.sleep(1)  # Kısa bir duraklama

    part2_prompt = """
    Now, start Part 2. Give me a cue card on the topic 'Describe a time you learned a new skill'.
    Tell me what the skill was, who you learned it from, and how you felt about it.
    Clearly state that I have one minute to prepare and then I should speak for 1 to 2 minutes.
    """
    question = examiner.ask_question(part2_prompt)
    speak_text(question)

    speak_text("Your 1-minute preparation time starts now.")
    time.sleep(60)  # Kullanıcıya hazırlanması için 1 dakika veriyoruz

    speak_text("Alright, your preparation time is up. You can start speaking now.")

    # Part 2'de kullanıcının uzun cevabını dinliyoruz.
    # Not: Bu fonksiyon ilk anlamlı duraklamada duracaktır.
    user_long_answer = listen_to_user()
    examiner.record_user_answer(user_long_answer)

    # --- PART 3: İki Yönlü Tartışma ---
    speak_text("Thank you. Now, in Part 3, we will discuss this topic more broadly.")
    time.sleep(1)

    part3_prompt = "Now, start Part 3. Ask me a deeper, more abstract question related to the Part 2 topic of 'learning new skills'."
    question = examiner.ask_question(part3_prompt)
    speak_text(question)

    # Part 3 için yaklaşık 4 soru-cevap döngüsü
    for i in range(4):
        user_answer = listen_to_user()
        examiner.record_user_answer(user_answer)

        if user_answer is None:
            continue

        if i < 3:
            # Kullanıcının son cevabına dayalı olarak yeni bir tartışma sorusu üretmesini istiyoruz
            next_prompt = "Based on my last answer, ask a follow-up discussion question that explores the topic further."
            question = examiner.ask_question(next_prompt)
            speak_text(question)

    # --- DEĞERLENDİRME ---
    speak_text(
        "Thank you. That is the end of the speaking test. I will now generate your feedback. Please check the console for your detailed report.")

    feedback = examiner.generate_final_feedback()
    print("\n" + "=" * 50)
    print(" IELTS SPEAKING TEST FEEDBACK REPORT")
    print("=" * 50 + "\n")
    print(feedback)
    print("\n" + "=" * 50)


# Programın ana başlangıç noktası
if __name__ == "__main__":
    run_speaking_test()