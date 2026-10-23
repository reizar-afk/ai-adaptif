import streamlit as st
import os
import yaml
import base64
from rag.query import Assistant
from rag.generate import answer

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Ambatron AI", layout="wide", initial_sidebar_state="expanded")

# --- FUNGSI BACKGROUND ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    # PAKAI NAMA FILE GAMBAR BARU LU
    img_base64 = get_base64_of_bin_file('d6193632d606fd315b6e1e368d6542df.jpg')
except:
    img_base64 = ""

# --- CSS TINGKAT DEWA (GLASSMORPHISM + ANIMASI) ---
st.markdown(f"""
<style>
    /* Import Font Inter (Font ChatGPT) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

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
    
    /* Overlay gelap elegan */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.75);
        z-index: -1;
    }}
    
    /* EFEK KACA (GLASSMORPHISM) di Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(30, 30, 30, 0.6) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Nama AI di kanan atas */
    .ai-name {{
        position: fixed;
        top: 15px;
        right: 25px;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 18px;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 8px 20px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Ilangin kotak/avatar bawaan chat */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 15px;
        animation: fadeIn 0.5s ease-in-out; /* Animasi Fade In */
    }}
    [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    
    /* Animasi Fade In */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* Teks chat */
    p, div, span {{
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
    }}
    
    /* Bikin Bubble Chat */
    .user-msg {{
        background: rgba(0, 100, 255, 0.6) !important; /* Warna biru buat user */
        padding: 12px 18px;
        border-radius: 15px 15px 0px 15px;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
        margin-bottom: 10px;
        backdrop-filter: blur(5px);
    }}
    .ai-msg {{
        background: rgba(255, 255, 255, 0.1) !important; /* Warna gelap buat AI */
        padding: 12px 18px;
        border-radius: 15px 15px 15px 0px;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
        margin-bottom: 10px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.05);
    }}
    
    /* Kolom input chat di bawah (Glassmorphism) */
    .stChatInput {{
        position: fixed;
        bottom: 25px;
        left: 50%;
        transform: translateX(-50%);
        width: 80%;
        max-width: 800px;
        background: rgba(40, 40, 40, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        z-index: 999;
    }}
    
    /* Ngilangin outline merah/kuning saat klik */
    *:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}
    .stChatInput textarea {{
        border: none !important;
        background: transparent !important;
    }}
</style>
<div class="ai-name">🤖 Ambatron</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🤖 Ambatron AI")
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

# Tampilin chat dengan class CSS khusus
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f'<div class="user-msg">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">{message["content"]}</div>', unsafe_allow_html=True)

# Input chat
if prompt := st.chat_input("Tanya apa aja..."):
    # Simpan & tampilin pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    # Generate jawaban AI
    with st.chat_message("assistant"):
        with st.spinner("Ambatron sedang berpikir..."):
            response = answer(assistant, prompt, "user1")
            st.markdown(f'<div class="ai-msg">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
