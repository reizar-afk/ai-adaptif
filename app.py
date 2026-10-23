import streamlit as st
import os
import yaml
import base64
import uuid
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

# --- CSS TINGKAT DEWA ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    #MainMenu, header, footer {{visibility: hidden;}}
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
    
    /* Sembunyiin sidebar bawaan, kita pake custom */
    [data-testid="stSidebar"] {{ display: none !important; }}
    
    /* HEADER BAR */
    .chatgpt-header {{
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background: rgba(20, 20, 20, 0.8); backdrop-filter: blur(15px);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 20px; z-index: 1000; border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .header-btn {{
        color: #ccc; font-size: 24px; cursor: pointer; text-decoration: none;
        background: none; border: none; padding: 5px;
    }}
    .header-btn:hover {{ color: #fff; }}
    .header-title {{ color: #fff; font-family: 'Inter'; font-weight: 600; font-size: 16px; }}
    
    .block-container {{ padding-top: 80px !important; padding-bottom: 100px !important; max-width: 800px; }}
    
    /* BUBBLE CHAT */
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
    
    /* INPUT CHAT */
    .stChatInput {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        width: 90%; max-width: 800px; background: rgba(40, 40, 40, 0.9) !important;
        backdrop-filter: blur(15px) !important; border-radius: 15px; border: none !important; z-index: 999;
    }}
    .stChatInput textarea {{ border: none !important; background: transparent !important; color: white !important; }}
    *:focus {{ outline: none !important; box-shadow: none !important; }}
    
    /* MENU SIDEBAR CUSTOM */
    .custom-sidebar {{
        position: fixed; top: 60px; left: 0; bottom: 0; width: 260px;
        background: rgba(20, 20, 20, 0.95); backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.1); z-index: 999;
        padding: 20px; overflow-y: auto;
    }}
    .sidebar-item {{
        color: #ccc; padding: 10px; border-radius: 8px; cursor: pointer;
        margin-bottom: 5px; font-family: 'Inter'; font-size: 14px;
        display: block; text-decoration: none;
    }}
    .sidebar-item:hover {{ background: rgba(255,255,255,0.1); color: white; }}
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT UNTUK RIWAYAT CHAT ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {} # Format: {id: {"title": str, "messages": []}}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# --- LOGIKA BUKA TUTUP SIDEBAR & CHAT BARU ---
query_params = st.query_params
if "action" in query_params:
    if query_params["action"] == "toggle_sidebar":
        st.session_state.show_sidebar = not st.session_state.show_sidebar
    elif query_params["action"] == "new_chat":
        st.session_state.current_chat_id = None
        st.session_state.show_sidebar = False
    elif query_params["action"].startswith("load_"):
        chat_id = query_params["action"].replace("load_", "")
        st.session_state.current_chat_id = chat_id
        st.session_state.show_sidebar = False
    
    # Bersihin URL biar ga looping
    st.query_params.clear()
    st.rerun()

# --- HEADER BAR ---
st.markdown(f"""
<div class="chatgpt-header">
    <a href="?action=toggle_sidebar" target="_self" class="header-btn">☰</a>
    <span class="header-title">🤖 Ambatron</span>
    <a href="?action=new_chat" target="_self" class="header-btn">✏️</a>
</div>
""", unsafe_allow_html=True)

# --- TAMPILIN SIDEBAR JIKA DIBUKA ---
if st.session_state.show_sidebar:
    st.markdown('<div class="custom-sidebar">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:white; font-family:Inter;'>Riwayat Chat</h3>", unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#aaa; font-size:14px;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        for chat_id, data in reversed(list(st.session_state.chat_sessions.items())):
            # Bikin link buat load chat
            st.markdown(f'<a href="?action=load_{chat_id}" target="_self" class="sidebar-item">💬 {data["title"]}</a>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIKA AI ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@st.cache_resource
def load_ai():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

assistant = load_ai()

# --- RENDER CHAT AKTIF ---
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
    # Kalau belum ada chat aktif, bikin chat baru
    if not st.session_state.current_chat_id:
        new_id = str(uuid.uuid4())[:6]
        st.session_state.current_chat_id = new_id
        # Ambil 20 huruf pertama sebagai judul
        title = prompt[:20] + ("..." if len(prompt) > 20 else "")
        st.session_state.chat_sessions[new_id] = {"title": title, "messages": []}
    
    chat_id = st.session_state.current_chat_id
    
    # Simpan pesan user
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    # Generate jawaban AI
    with st.spinner("Ambatron sedang berpikir..."):
        response = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "assistant", "content": response})
