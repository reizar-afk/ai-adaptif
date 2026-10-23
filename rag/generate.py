
import os
from query import Assistant
from google import genai

def answer(assistant, question, user_id):
    ctx = assistant.build_context(question, user_id)
    prompt = f"Konteks:\n{ctx['context']}\n\nPertanyaan: {ctx['question']}"
    
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-1.5-flash-8b", 
        contents=prompt,
    )
    return response.text
