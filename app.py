import streamlit as st
import os
import yaml
from rag.query import Assistant
from rag.generate import answer

# --- CONFIG TAMPILAN CHATGPT ---
st.set_page_config(page_title="Reii Stru", page_icon="🗿", layout="centered")

# CSS Biar Mirip ChatGPT
st.markdown("""
<style>
    /* Sembunyiin header Streamlit & menu */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Background utama gelap */
    .stApp {
        background-color: #212121;
    }
    
    /* Warna teks putih */
    h1, p, div {
        color: #ececec !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Bikin input chat nempel di bawah (kayak ChatGPT) */
    .stChatInput {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #2f2f2f;
        padding: 15px;
        z-index: 999;
    }
    
    /* Bubble chat user */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #2f2f2f;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    /* Bubble chat AI */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: transparent;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA AI ---
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

st.title("🗿 Ambasing De Tukam")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

assistant = load_ai()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilin chat sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input chat
if prompt := st.chat_input("Ketik pertanyaanmu di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ambasing Lagi Mikir Dulu..."):
            response = answer(assistant, prompt, "user1")
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
