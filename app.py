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
    
    /* Sembunyiin semua elemen bawaan Streamlit */
    #MainMenu, header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
        display: none !important; visibility: hidden !important;
    }}
    
    /* Background */
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
    
    /* Bubble Chat */
    .chat-bubble-user {{
        background: linear-gradient(135deg, #0052D4, #4364F7); padding: 12px 18px; border-radius: 20px 20px 4px 20px;
        display: inline-block; max-width: 85%; float: right; clear: both; color: white;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    .chat-bubble-ai {{
        background: rgba(30, 30, 30, 0.85); backdrop-filter: blur(10px); padding: 12px 18px; border-radius: 20px 20px 20px 4px;
        display: inline-block; max-width: 85%; float: left; clear: both; color: #ececec;
        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }}
    
    /* Input Chat */
    .stChatInput {{
        position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
        width: 85%; max-width: 800px; background: rgba(25, 25, 25, 0.8) !important;
        backdrop-filter: blur(15px) !important; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
        z-index: 999;
    }}
    .stChatInput textarea {{ border: none !important; background: transparent !important; color: white !important; }}
    *:focus {{ outline: none !important; box-shadow: none !important; }}

    /* HEADER PALSU */
    .fake-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: rgba(15, 15, 15, 0.95); backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 990;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 20px; box-sizing: border-box;
    }}
    .fake-header .title {{ color: #fff; font-size: 18px; font-weight: 600; }}
    
    /* Tombol yang di-overlay di atas header */
    div[data-testid="column"]:nth-of-type(1) {{
        position: fixed !important; top: 12px !important; left: 15px !important; z-index: 1000 !important; width: 40px !important;
    }}
    div[data-testid="column"]:nth-of-type(2) {{
        position: fixed !important; top: 12px !important; right: 15px !important; z-index: 1000 !important; width: 110px !important;
    }}
    div[data-testid="column"] button {{
        background: transparent !important; border: none !important; color: white !important;
        font-size: 24px !important; padding: 0 !important;
    }}
    div[data-testid="column"]:nth-of-type(2) button {{
        font-size: 14px !important; background: rgba(255,255,255,0.1) !important; 
        padding: 6px 12px !important; border-radius: 15px !important; width: 100% !important;
    }}

    /* OVERLAY HISTORY */
    .history-overlay {{
        position: fixed; top: 60px; left: 0; width: 280px; height: calc(100vh - 60px);
        background: rgba(20, 20, 20, 0.95); backdrop-filter: blur(20px);
        z-index: 1001; padding: 20px; overflow-y: auto;
        border-right: 1px solid rgba(255,255,255,0.1); box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }}
</style>

<!-- TAMPILAN HEADER -->
<div class="fake-header">
    <div style="width: 40px;"></div>
    <div class="title">🤖 Ambatron</div>
    <div style="width: 110px;"></div>
</div>
""", unsafe_allow_html=True)

# --- STATE ---
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "show_history" not in st.session_state: st.session_state.show_history = False

# --- TOMBOL ASLI (DI-OVERLAY KE HEADER) ---
col1, col2 = st.columns([1, 10])
with col1:
    if st.button("☰", key="toggle_hist"):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()
with col2:
    if st.button("+ Chat", key="new_chat_btn"):
        st.session_state.current_chat_id = None
        st.session_state.show_history = False
        st.rerun()

# --- OVERLAY HISTORY ---
if st.session_state.show_history:
    st.markdown('<div class="history-overlay">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:white;'>Riwayat Chat</h3>", unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#aaa;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        for cid, cdata in reversed(list(st.session_state.chat_sessions.items())):
            if st.button(f"💬 {cdata['title']}", key=f"load_{cid}"):
                st.session_state.current_chat_id = cid
                st.session_state.show_history = False
                st.rerun()
    
    # Tombol Tutup Manual (kalau klik blank space susah)
    if st.button("❌ Tutup Riwayat", key="close_hist"):
        st.session_state.show_history = False
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIKA AI (FIX ERROR) ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Pake fungsi cache yang bener biar ga error
@st.cache_resource
def load_assistant():
    cfg = yaml.safe_load(open('config.yaml'))
    return Assistant(cfg)

try:
    assistant = load_assistant()
except Exception as e:
    st.error(f"Gagal load database: {e}")
    st.stop()

# --- RENDER CHAT ---
msgs = []
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
    msgs = st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"]

for m in msgs:
    if m["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{m["content"]}</div>', unsafe_allow_html=True)

# --- INPUT CHAT ---
if prompt := st.chat_input("Tanya apa aja..."):
    if not st.session_state.current_chat_id:
        nid = str(uuid.uuid4())[:6]
        st.session_state.current_chat_id = nid
        st.session_state.chat_sessions[nid] = {"title": prompt[:20]+"...", "messages": []}
    
    cid = st.session_state.current_chat_id
    st.session_state.chat_sessions[cid]["messages"].append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("..."):
        res = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{res}</div>', unsafe_allow_html=True)
    
    st.session_state.chat_sessions[cid]["messages"].append({"role": "assistant", "content": res})
