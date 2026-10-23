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
    img_base64 = get_base64_of_bin_file('d6193632d606fd315b6e1e368d6542df.jpg')
except:
    img_base64 = ""

# --- CSS TINGKAT DEWA (FIX IKON & TAMPILAN) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.65); /* Overlay dibikin lebih transparan biar Gojo-nya kelihatan */
        z-index: -1;
    }}
    
    /* SIDEBAR KACA */
    [data-testid="stSidebar"] {{
        background: rgba(20, 20, 20, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* HILANGIN TOTAL IKON MERAH/ORANGE (AVATAR) */
    [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    
    /* ILANGIN KOTAK HITAM BAWAAN STREAMLIT */
    [data-testid="stChatMessage"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 10px;
        animation: fadeIn 0.3s ease-in-out;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(5px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* BUBBLE CHAT USER (BIRU) */
    .chat-bubble-user {{
        background: rgba(0, 100, 255, 0.8);
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        display: inline-block;
        max-width: 80%;
        float: right;
        clear: both;
        color: white;
        font-family: 'Inter', sans-serif;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    
    /* BUBBLE CHAT AI (GELAP) */
    .chat-bubble-ai {{
        background: rgba(50, 50, 50, 0.8);
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        display: inline-block;
        max-width: 80%;
        float: left;
        clear: both;
        color: #ececec;
        font-family: 'Inter', sans-serif;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    
    /* NAMA AI DI KANAN ATAS */
    .ai-name {{
        position: fixed;
        top: 15px;
        right: 25px;
        color: #fff;
        font-weight: 600;
        font-size: 16px;
        z-index: 1000;
        background: rgba(255,255,255,0.1);
        padding: 6px 15px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }}
    
    /* INPUT CHAT BAWAH */
    .stChatInput {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 75%;
        max-width: 800px;
        background: rgba(30, 30, 30, 0.8) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 25px;
        border: 1px solid rgba(255,255,255,0.1);
        z-index: 999;
    }}
    
    .stChatInput textarea {{
        border: none !important;
        background: transparent !important;
        color: white !important;
    }}
    
    /* NGILANGIN GARIS MERAH DI INPUT */
    *:focus {{ outline: none !important; box-shadow: none !important; }}
</style>
<div class="ai-name">🤖 Ambatron</div>
""", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
with st.sidebar:
    st.markdown("### 🤖 Ambatron AI")
    st.button("➕ Mulai Chat Baru", use_container_width=True)
    st.markdown("---")
    st.markdown("**Riwayat Chat**")
    # Dummy riwayat
    st.markdown("💬 Perbedaan Rokok & Vape")
    st.markdown("💻 Cara Bikin Loop Python")
    st.markdown("📝 Resep Nasi Goreng")
    st.markdown("---")
    st.markdown("**Pengaturan**")
    st.button("⚙️ Buka Pengaturan", use_container_width=True)

# --- LOGIKA AI ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

assistant = load_ai()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- RENDER CHAT ---
for message in st.session_state.messages:
    # Kita pake st.empty() biar bener-bener ga nge-render avatar
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT CHAT ---
if prompt := st.chat_input("Tanya apa aja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Ambatron sedang berpikir..."):
        response = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
