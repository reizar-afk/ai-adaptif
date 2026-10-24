import streamlit as st
import os
import yaml
import base64
import uuid
from rag.query import Assistant
from rag.generate import answer

st.set_page_config(page_title="Ambatron AI", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")

# --- FUNGSI BACKGROUND ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    img_base64 = get_base64_of_bin_file('d6193632d606fd315b6e1e368d6542df.jpg')
except:
    img_base64 = ""

# --- CSS (FIX TEKS KELUAR KOTAK) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    header {{
        background: rgba(10, 10, 10, 0.95) !important;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }}
    
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.6); z-index: -1;
    }}
    
    .block-container {{ padding-top: 80px !important; padding-bottom: 100px !important; max-width: 800px; }}
    
    .custom-title {{
        position: fixed; top: 15px; left: 0; width: 100%; text-align: center;
        color: white; font-family: 'Inter'; font-weight: 600; font-size: 20px;
        z-index: 990; pointer-events: none; text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }}

    [data-testid="stSidebar"] {{
        background: rgba(20, 20, 20, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
        z-index: 1002 !important;
    }}
    
    .stButton button {{
        width: 100%; text-align: left; background: rgba(255,255,255,0.05) !important; 
        color: white !important; border: none !important; padding: 10px !important;
        border-radius: 8px !important; margin-bottom: 5px;
    }}
    .stButton button:hover {{ background: rgba(255,255,255,0.15) !important; }}

    .chat-bubble-user {{
        background: linear-gradient(135deg, #0052D4, #4364F7); padding: 12px 18px; border-radius: 20px 20px 4px 20px;
        display: inline-block; max-width: 85%; float: right; clear: both; color: white;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        word-wrap: break-word; /* Biar teks panjang turun ke bawah */
    }}
    .chat-bubble-ai {{
        background: rgba(30, 30, 30, 0.85); backdrop-filter: blur(10px); padding: 12px 18px; border-radius: 20px 20px 20px 4px;
        display: inline-block; max-width: 85%; float: left; clear: both; color: #ececec;
        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        overflow-x: auto; /* Biar tabel/kode bisa di-scroll, ga keluar kotak */
        word-wrap: break-word; /* Biar teks panjang turun ke bawah */
    }}
    
    /* Bikin tabel di dalam chat biar rapi */
    .chat-bubble-ai table {{
        width: 100% !important;
        border-collapse: collapse;
        margin: 10px 0;
    }}
    .chat-bubble-ai th, .chat-bubble-ai td {{
        border: 1px solid rgba(255,255,255,0.2);
        padding: 8px;
        text-align: left;
    }}
    
    .stChatInput {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        width: 85%; max-width: 800px; background: rgba(25, 25, 25, 0.8) !important;
        backdrop-filter: blur(15px) !important; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
        z-index: 999;
    }}
    .stChatInput textarea {{ border: none !important; background: transparent !important; color: white !important; }}
    *:focus {{ outline: none !important; box-shadow: none !important; }}
</style>

<div class="custom-title">🤖 Ambatron</div>
""", unsafe_allow_html=True)

# --- LOGIKA STATE ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "is_new_chat" not in st.session_state:
    st.session_state.is_new_chat = True

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color:white;'>🤖 Ambatron AI</h3>", unsafe_allow_html=True)
    
    if st.button("➕ Mulai Chat Baru", key="new_chat_sidebar"):
        st.session_state.current_chat_id = None
        st.session_state.is_new_chat = True
        st.rerun()
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#aaa;'>Riwayat Chat</p>", unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#666; font-size:12px;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        for cid, cdata in reversed(list(st.session_state.chat_sessions.items())):
            if st.button(f"💬 {cdata['title']}", key=f"load_{cid}"):
                st.session_state.current_chat_id = cid
                st.session_state.is_new_chat = False
                st.rerun()

# --- LOGIKA AI ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

try:
    cfg = yaml.safe_load(open('config.yaml'))
    @st.cache_resource
    def load_assistant():
        return Assistant(cfg)
    assistant = load_assistant()
except Exception as e:
    st.warning("⚠️ Database sedang sibuk. Klik 'Manage app' -> 'Reboot app' sekali lagi.")
    st.stop()

# --- RENDER CHAT ---
msgs = []
if not st.session_state.is_new_chat and st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
    msgs = st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"]

for m in msgs:
    if m["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{m["content"]}</div>', unsafe_allow_html=True)

# --- INPUT CHAT ---
if prompt := st.chat_input("Tanya apa aja..."):
    if st.session_state.is_new_chat or not st.session_state.current_chat_id:
        new_id = str(uuid.uuid4())[:6]
        st.session_state.current_chat_id = new_id
        st.session_state.is_new_chat = False
        title = prompt[:20] + ("..." if len(prompt) > 20 else "")
        st.session_state.chat_sessions[new_id] = {"title": title, "messages": []}
    
    chat_id = st.session_state.current_chat_id
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("..."):
        res = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{res}</div>', unsafe_allow_html=True)
    
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "assistant", "content": res})
