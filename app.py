import streamlit as st
import os
import yaml
import base64
from rag.query import Assistant
from rag.generate import answer

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Reii Stru", layout="wide", initial_sidebar_state="expanded")

# --- FUNGSI BACKGROUND ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    img_base64 = get_base64_of_bin_file('bg.jpg')
except:
    img_base64 = "" # Fallback kalau gambar nggak ada

# --- CSS TAMPILAN CHATGPT ---
st.markdown(f"""
<style>
    /* Sembunyiin header & footer bawaan Streamlit */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Background utama */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Overlay gelap biar elegan */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.85); /* Lebih gelap biar teks jelas */
        z-index: -1;
    }}
    
    /* Sidebar kiri (seperti ChatGPT) */
    [data-testid="stSidebar"] {{
        background-color: #202123 !important;
        border-right: 1px solid #444;
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
    
    /* Ilangin kotak/avatar bawaan chat */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 20px;
    }}
    [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    
    /* Teks chat */
    p, div, span {{
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
    }}
    
    /* Input chat di bawah */
    .stChatInput {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        max-width: 800px;
        background-color: #2f2f2f;
        border-radius: 15px;
        z-index: 999;
    }}
    
    /* Ngilangin outline merah/kuning saat klik */
    *:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}
    .stChatInput textarea {{
        border: none !important;
    }}
</style>
<div class="ai-name">🤖 Ambatron</div>
""", unsafe_allow_html=True)

# --- SIDEBAR (MENU KIRI) ---
with st.sidebar:
    st.markdown("### 🤖 Ambatron Chat")
    st.button("➕ New Chat", use_container_width=True)
    st.markdown("---")
    st.markdown("**Riwayat Chat**")
    st.markdown("- Perbedaan Rokok & Vape\n- Coding Python\n- Resep Makanan")
    st.markdown("---")
    st.markdown("**Pengaturan**")
    st.button("⚙️ Settings", use_container_width=True)

# --- LOGIKA AI ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

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
