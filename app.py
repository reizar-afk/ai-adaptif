import streamlit as st
import os
import yaml
import base64
from rag.query import Assistant
from rag.generate import answer

st.set_page_config(page_title="Ambatron AI", layout="centered", initial_sidebar_state="collapsed")

# --- FUNGSI BACKGROUND ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    img_base64 = get_base64_of_bin_file('d6193632d606fd315b6e1e368d6542df.jpg')
except:
    img_base64 = ""

# --- CSS TINGKAT DEWA (HEADER CHATGPT) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    /* Sembunyiin elemen bawaan */
    #MainMenu, header, footer {{visibility: hidden;}}
    
    /* Background */
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
        background: rgba(0, 0, 0, 0.6);
        z-index: -1;
    }}
    
    /* Sembunyiin sidebar bawaan Streamlit */
    [data-testid="stSidebar"] {{ display: none !important; }}
    
    /* HEADER BAR MELAYANG (Mirip ChatGPT) */
    .chatgpt-header {{
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 60px;
        background: rgba(20, 20, 20, 0.8);
        backdrop-filter: blur(15px);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 20px;
        z-index: 1000;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .header-left {{ display: flex; align-items: center; gap: 15px; }}
    .header-icon {{
        color: #ccc;
        font-size: 20px;
        cursor: pointer;
        text-decoration: none;
    }}
    .header-icon:hover {{ color: #fff; }}
    .header-title {{
        color: #fff;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 16px;
    }}
    
    /* Jarak biar chat ga ketutup header */
    .block-container {{
        padding-top: 80px !important;
        padding-bottom: 100px !important;
        max-width: 800px;
    }}
    
    /* BUBBLE CHAT USER */
    .chat-bubble-user {{
        background: rgba(0, 100, 255, 0.8);
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        display: inline-block;
        max-width: 85%;
        float: right;
        clear: both;
        color: white;
        font-family: 'Inter', sans-serif;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    
    /* BUBBLE CHAT AI */
    .chat-bubble-ai {{
        background: rgba(40, 40, 40, 0.9);
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        display: inline-block;
        max-width: 85%;
        float: left;
        clear: both;
        color: #ececec;
        font-family: 'Inter', sans-serif;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    
    /* INPUT CHAT BAWAH */
    .stChatInput {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 800px;
        background: rgba(40, 40, 40, 0.9) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 15px;
        border: none !important;
        z-index: 999;
    }}
    .stChatInput textarea {{
        border: none !important;
        background: transparent !important;
        color: white !important;
    }}
    *:focus {{ outline: none !important; box-shadow: none !important; }}
</style>

<!-- HEADER BAR -->
<div class="chatgpt-header">
    <div class="header-left">
        <!-- Tombol Riwayat (Kiri) -->
        <a href="?menu=history" target="_self" class="header-icon" title="Riwayat Chat">☰</a>
        <span class="header-title">🤖 Ambatron</span>
    </div>
    <!-- Tombol Chat Baru (Kanan) -->
    <a href="?menu=new" target="_self" class="header-icon" title="Mulai Chat Baru">✏️</a>
</div>
""", unsafe_allow_html=True)

# --- LOGIKA MENU RIWAYAT / CHAT BARU ---
query_params = st.query_params
if "menu" in query_params:
    if query_params["menu"] == "history":
        st.info("📜 **Riwayat Chat:**\n- Perbedaan Rokok & Vape\n- Coding Python\n- Resep Makanan")
    elif query_params["menu"] == "new":
        st.session_state.messages = [] # Kosongin chat
        st.success("✨ Chat baru dimulai!")

# --- LOGIKA AI ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

assistant = load_ai()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilin Chat
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{message["content"]}</div>', unsafe_allow_html=True)

# Input Chat
if prompt := st.chat_input("Tanya apa aja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Ambatron sedang berpikir..."):
        response = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
