import streamlit as st
import os
import yaml
import base64
import uuid
from rag.query import Assistant
from rag.generate import answer

# 1. Set page config (pakai sidebar bawaan)
st.set_page_config(page_title="Ambatron AI", layout="centered", initial_sidebar_state="expanded")

# 2. Fungsi Background
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    img_base64 = get_base64_of_bin_file('d6193632d606fd315b6e1e368d6542df.jpg')
except:
    img_base64 = ""

# 3. CSS (Tampilan persis kayak SS lu)
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
    }}
    .chat-bubble-ai {{
        background: rgba(30, 30, 30, 0.85); backdrop-filter: blur(10px); padding: 12px 18px; border-radius: 20px 20px 20px 4px;
        display: inline-block; max-width: 85%; float: left; clear: both; color: #ececec;
        margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 10px rgba(0,0,0,0.3);
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

# 4. State Management
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {} # Format: {id: {"title": "...", "messages": [...]}}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# 5. SIDEBAR MENU
with st.sidebar:
    st.markdown("<h3 style='color:white;'>🤖 Ambatron AI</h3>", unsafe_allow_html=True)
    
    # --- LOGIKA TOMBOL CHAT BARU ---
    if st.button("➕ Mulai Chat Baru", key="new_chat_sidebar"):
        st.session_state.current_chat_id = None # Reset ke kosong (mulai chat baru)
        st.rerun() # Refresh biar layar bersih
        
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#aaa;'>Riwayat Chat</p>", unsafe_allow_html=True)
    
    # --- LOGIKA RIWAYAT CHAT ---
    if not st.session_state.chat_sessions:
        st.markdown("<p style='color:#666; font-size:12px;'>Belum ada riwayat.</p>", unsafe_allow_html=True)
    else:
        # Munculin list riwayat dari yang paling baru
        for cid, cdata in reversed(list(st.session_state.chat_sessions.items())):
            if st.button(f"💬 {cdata['title']}", key=f"load_{cid}"):
                st.session_state.current_chat_id = cid # Pindah ke chat lama
                st.rerun()

# 6. Logika AI
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

# 7. Render Chat Aktif
msgs = []
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
    msgs = st.session_state.chat_sessions[st.session_state.current_chat_id]["messages"]

for m in msgs:
    if m["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{m["content"]}</div>', unsafe_allow_html=True)

# 8. Input Chat
if prompt := st.chat_input("Tanya apa aja..."):
    # Kalau lagi ga ada chat aktif, bikin sesi baru
    if not st.session_state.current_chat_id:
        new_id = str(uuid.uuid4())[:6]
        st.session_state.current_chat_id = new_id
        # Ambil 20 huruf pertama sebagai judul riwayat
        title = prompt[:20] + ("..." if len(prompt) > 20 else "")
        st.session_state.chat_sessions[new_id] = {"title": title, "messages": []}
    
    chat_id = st.session_state.current_chat_id
    
    # Simpan pesan user
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    # Generate jawaban AI
    with st.spinner("..."):
        res = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{res}</div>', unsafe_allow_html=True)
    
    # Simpan jawaban AI
    st.session_state.chat_sessions[chat_id]["messages"].append({"role": "assistant", "content": res})
