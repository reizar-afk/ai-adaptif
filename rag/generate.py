import os
from groq import Groq
from query import Assistant

def answer(assistant, question, user_id):
    ctx = assistant.build_context(question, user_id)
    prompt = f"Konteks:\n{ctx['context']}\n\nPertanyaan: {ctx['question']}"
    
    # Panggil Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Kamu adalah asisten AI yang pintar dan ramah. Jawab dalam bahasa Indonesia."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-120b",
    )
    return chat_completion.choices[0].message.content
