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

# --- CSS ---
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
    
    /* Sembunyiin sidebar bawaan Streamlit */
    [data-testid="stSidebar"] {{ display: none !important; }}
    
    /* HEADER BAR */
    .chatgpt-header {{
        position: fixed; top: 0; left: 0; right: 0; height: 60px;
        background: rgba(20, 20, 20, 0.9); backdrop-filter: blur(15px);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 15px; z-index: 1000; border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .header-btn {{
        color: #ccc; font-size: 24px; cursor: pointer; text-decoration: none;
        background: none; border: none; padding: 5px; display: flex; align-items: center; justify-content: center;
    }}
    .header-btn:hover {{ color: #fff; }}
    .header-title {{ color: #fff; font-family: 'Inter'; font-weight: 600; font-size: 16px; flex-grow: 1; text-align: center; }}
    
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

    /* SIDEBAR PANEL (Mengambang di atas chat) */
    .sidebar-panel {{
        position: fixed; top: 60px; left: 0; width: 280px; height: calc(100vh - 60px);
        background: rgba(25, 25, 25, 0.95); backdrop-filter: blur(20px);
        z-index: 1001; padding: 20px; overflow-y: auto;
        border-right: 1px solid rgba(255,255,255,0.1);
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
    }}
    .sidebar-header {{ color: white; font-family: 'Inter'; font-size: 18px; margin-bottom: 20px; font-weight: bold; }}
    .sidebar-item {{
        color: #ccc; padding: 12px; border-radius: 8px; cursor: pointer;
        margin-bottom: 8px; font-family: 'Inter'; font-size: 14px;
        display: block; text-decoration: none; border: 1px solid rgba(255,255,255,0.05);
    }}
    .sidebar-item:hover {{ background: rgba(255,255,255,0.1); color: white; }}
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Gunakan session_state untuk toggle sidebar tanpa reload
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = False

# --- HEADER BAR ---
# Pakai tombol python agar tidak reload halaman
col1, col2, col3 = st.columns([1, 8, 1])
with col1:
    if st.button("☰", key="toggle_menu"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar
with col2:
    st.markdown('<div style="text-align: center; color: white; font-family: Inter; font-weight: bold; margin-top: 5px;">🤖 Ambatron</div>', unsafe_allow_html=True)
with col3:
    if st.button("✏️", key="new_chat"):
        st.session_state.current_chat_id = None
        st.session_state.show_sidebar = False
        st.rerun()

# --- SIDEBAR PANEL ---
if st.session_state.show_sidebar:
    st.markdown('<div class="sidebar-panel">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">Riwayat Chat</div>', unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#aaa; font-size:14px;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        for chat_id, data in reversed(list(st.session_state.chat_sessions.items())):
            if st.button(f"💬 {data['title']}", key=f"load_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.show_sidebar = False
                st.rerun()
    
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
