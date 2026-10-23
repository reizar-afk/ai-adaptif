import streamlit as st
import os
import yaml
import base64
from rag.query import Assistant
from rag.generate import answer

st.set_page_config(page_title="AI Reizar", layout="centered", initial_sidebar_state="collapsed")

# --- FUNGSI UNTUK BACKGROUND GAMBAR ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Ganti 'bg.jpg' kalau nama file foto lu beda
img_base64 = get_base64_of_bin_file('bg.jpg') 

# --- CSS TAMPILAN CHATGPT ---
st.markdown(f"""
<style>
    /* Sembunyiin header bawaan Streamlit */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Background pakai foto lu */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Overlay gelap biar tulisan kebaca */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        z-index: -1;
    }}
    
    /* Container chat biar di tengah */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 100px !important;
        max-width: 800px;
    }}
    
    /* Nama AI di kanan atas */
    .ai-name {{
        position: fixed;
        top: 15px;
        right: 20px;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-weight: bold;
        font-size: 16px;
        z-index: 1000;
        background: rgba(0,0,0,0.5);
        padding: 5px 15px;
        border-radius: 20px;
    }}
    
    /* Bikin bubble chatnya transparan dan rapi */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }}
    
    /* Bubble User */
    [data-testid="stChatMessage"]:has(div[data-testid="stMarkdownContainer"] p:nth-child(1)) {{
        /* Trik CSS buat bedain user & AI susah, jadi kita bikin seragam aja */
    }}
    
    /* Teks chat biar putih bersih */
    p, div, span {{
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Kolom input di bawah */
    .stChatInput {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 800px;
        background-color: #2f2f2f;
        border-radius: 15px;
        z-index: 999;
    }}
</style>
<div class="ai-name">🤖 Reii AI</div>
""", unsafe_allow_html=True)

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

assistant = load_ai()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanya apa aja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("..."):
            response = answer(assistant, prompt, "user1")
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
