import streamlit as st
import os
import yaml
import base64
import uuid
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

# --- CSS TINGKAT DEWA ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* Sembunyiin header bawaan Streamlit (tapi kita butuh tombol panahnya) */
    #MainMenu {{visibility: hidden;}}
    header {{background: transparent !important;}}
    footer {{visibility: hidden;}}
    
    /* Background */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.6); z-index: -1;
    }}
    
    /* Sidebar Kaca */
    [data-testid="stSidebar"] {{
        background: rgba(20, 20, 20, 0.9) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }}
    
    /* Header Title di Tengah */
    .app-header {{
        position: fixed; top: 10px; left: 0; width: 100%;
        text-align: center; color: white; font-family: 'Inter'; font-weight: 600; font-size: 20px;
        z-index: 1000; pointer-events: none;
    }}
    
    /* Bubble Chat */
    .chat-bubble-user {{
        background: rgba(0, 100, 255, 0.8); padding: 12px 18px; border-radius: 20px 20px 5px 20px;
        display: inline-block; max-width: 85%; float: right; clear: both; color: white;
        font-family: 'Inter'; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    .chat-bubble-ai {{
        background: rgba(40, 40, 40, 0.9); padding: 12px 18px; border-radius: 20px 20px 20px 5px;
        display: inline-block; max-width: 85%; float: left; clear: both; color: #ececec;
        font-family: 'Inter'; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    
    /* Input Chat */
    .stChatInput {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 800px; background: rgba(40, 40, 40, 0.9) !important;
        backdrop-filter: blur(15px) !important; border-radius: 15px; border: none !important; z-index: 999;
    }}
    .stChatInput textarea {{ border: none !important; background: transparent !important; color: white !important; }}
    *:focus {{ outline: none !important; box-shadow: none !important; }}
    
    /* Tombol Sidebar Menu */
    .stButton button {{
        width: 100%; text-align: left; background: transparent !important; 
        color: white !important; border: none !important; padding: 10px !important;
    }}
    .stButton button:hover {{ background: rgba(255,255,255,0.1) !important; }}
</style>

<!-- Judul di Tengah Atas -->
<div class="app-header">🤖 Ambatron</div>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- SIDEBAR MENU (Riwayat) ---
with st.sidebar:
    st.markdown("<h2 style='color:white; font-family:Inter;'>🤖 Ambatron AI</h2>", unsafe_allow_html=True)
    
    # Tombol New Chat
    if st.button("➕ Mulai Chat Baru", key="new_chat_btn"):
        st.session_state.current_chat_id = None
        st.rerun()
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#aaa; font-family:Inter; font-size:14px;'>Riwayat Chat</p>", unsafe_allow_html=True)

    # List Riwayat
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#666; font-size:12px;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        for chat_id, data in reversed(list(st.session_state.chat_sessions.items())):
            if st.button(f"💬 {data['title']}", key=f"load_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- LOGIKA AI ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

assistant = load_ai()

# --- RENDER CHAT ---
current_messages = []
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
    current_messages = st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"]

for message in current_messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT CHAT ---
if prompt := st.chat_input("Tanya apa aja..."):
    if not st.session_state.current_chat_id:
        new_id = str(uuid.uuid4())[:6]
        st.session_state.current_chat_id = new_id
        title = prompt[:25] + ("..." if len(prompt) > 25 else "")
        st.session_state.chat_sessions[new_id] = {"title": title, "messages": []}
    
    chat_id = st.session_state.current_chat_id
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Ambatron sedang berpikir..."):
        response = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "assistant", "content": response})
