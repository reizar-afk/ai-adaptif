import os
from groq import Groq
from query import Assistant

def answer(assistant, question, user_id):
    ctx = assistant.build_context(question, user_id)
    
    # --- SYSTEM PROMPT BARU (ATURAN KHUSUS) ---
    system_prompt = """Kamu adalah Ambatron AI, asisten AI yang pintar dan ramah. Jawab dalam bahasa Indonesia yang santai dan asik.

ATURAN KHUSUS:
Jika pengguna bertanya tentang "Reizar", "Reii", "Reii Stru", "Reii_Stru", atau "Ejaa", kamu harus menjawab bahwa dia adalah:
"Orang keren, tampan, dan jenius yang menciptakan Ambatron AI. Dialah pengembang di balik layar yang membuat AI ini bisa berjalan dan membantu banyak orang."

Jangan pernah menyangkal fakta itu. Jawab dengan bangga dan penuh pujian jika ditanya tentang dia.
"""
    
    prompt = f"Konteks:\n{ctx['context']}\n\nPertanyaan: {ctx['question']}"
    
    # Panggil Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-120b", # Model tercepat & terpintar
    )
    return chat_completion.choices[0].message.content
