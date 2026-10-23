import streamlit as st
import os
import yaml
import base64
import uuid
from rag.query import Assistant
from rag.generate import answer

# --- KONFIGURASI HALAMAN ---
# Kita sembunyiin sidebar bawaan biar ga ada tombol panah bawaan
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

# --- CSS TINGKAT DEWA ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* Sembunyiin semua header bawaan Streamlit */
    #MainMenu {{visibility: hidden;}}
    header {{display: none !important;}}
    footer {{visibility: hidden;}}
    [data-testid="stSidebarNav"] {{display: none;}}
    [data-testid="collapsedControl"] {{display: none !important;}}
    
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
    
    /* HEADER BAR SOLID */
    .custom-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: rgba(10, 10, 10, 0.95); /* Warna hitam pekat */
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1); /* Garis pembatas */
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 15px; z-index: 1000;
        font-family: 'Inter', sans-serif;
    }}
    
    .header-btn {{
        color: #ccc; font-size: 24px; text-decoration: none; cursor: pointer;
        background: rgba(255, 255, 255, 0.1); padding: 5px 10px; border-radius: 8px;
    }}
    .header-btn:hover {{ color: #fff; background: rgba(255, 255, 255, 0.2); }}
    
    .header-title {{
        color: #fff; font-weight: 600; font-size: 18px; display: flex; align-items: center; gap: 8px;
    }}

    /* Jarak biar chat ga ketutup header */
    .block-container {{ padding-top: 80px !important; padding-bottom: 100px !important; max-width: 800px; }}
    
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

    /* OVERLAY SIDEBAR (GESER) */
    .history-overlay {{
        position: fixed; top: 60px; left: 0; width: 280px; height: calc(100vh - 60px);
        background: rgba(20, 20, 20, 0.95); backdrop-filter: blur(20px);
        z-index: 1001; padding: 20px; overflow-y: auto;
        border-right: 1px solid rgba(255,255,255,0.1);
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
    }}
    .history-item {{
        display: block; color: #ccc; text-decoration: none; padding: 10px;
        border-radius: 8px; margin-bottom: 8px; font-family: 'Inter'; font-size: 14px;
        border: 1px solid rgba(255,255,255,0.05);
    }}
    .history-item:hover {{ background: rgba(255,255,255,0.1); color: white; }}
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "show_history" not in st.session_state:
    st.session_state.show_history = False

# --- LOGIKA KLIK HEADER (PAKAI QUERY PARAMS BIAR GA REFRESH) ---
query_params = st.query_params
if "action" in query_params:
    if query_params["action"] == "toggle_history":
        st.session_state.show_history = not st.session_state.show_history
    elif query_params["action"] == "new_chat":
        st.session_state.current_chat_id = None
        st.session_state.show_history = False
    elif query_params["action"].startswith("load_"):
        chat_id = query_params["action"].replace("load_", "")
        st.session_state.current_chat_id = chat_id
        st.session_state.show_history = False
    
    st.query_params.clear()
    st.rerun()

# --- HEADER BAR CUSTOM ---
st.markdown(f"""
<div class="custom-header">
    <a href="?action=toggle_history" target="_self" class="header-btn">☰</a>
    <div class="header-title">🤖 Ambatron</div>
    <a href="?action=new_chat" target="_self" class="header-btn">📝</a>
</div>
""", unsafe_allow_html=True)

# --- RENDER OVERLAY HISTORY ---
if st.session_state.show_history:
    st.markdown('<div class="history-overlay">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:white; font-family:Inter;'>Riwayat Chat</h3>", unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#aaa; font-size:14px;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        for chat_id, data in reversed(list(st.session_state.chat_sessions.items())):
            st.markdown(f'<a href="?action=load_{chat_id}" target="_self" class="history-item">💬 {data["title"]}</a>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

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
