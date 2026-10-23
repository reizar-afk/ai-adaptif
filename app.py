import streamlit as st
import os
import sys
import yaml

# Tambahin path folder tempat file ini berada
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from rag.query import Assistant
from rag.generate import answer

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Adaptif LO", page_icon="🤖")
st.title("🤖 AI Pengetahuan & Coding")
st.write("Tanya apa aja soal pengetahuan umum atau coding.")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open(os.path.join(current_dir, 'config.yaml')))
    return Assistant(cfg)

assistant = load_ai()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ketik pertanyaanmu di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AI sedang berpikir..."):
            response = answer(assistant, prompt, "user1")
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
