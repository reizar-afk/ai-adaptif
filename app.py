import streamlit as st
import os
import yaml
import base64
import streamlit.components.v1 as components
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
    #MainMenu, header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] {{ display: none !important; }}
    
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }}
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.6); z-index: -1;
    }}
    
    .block-container {{ padding-top: 60px !important; padding-bottom: 100px !important; max-width: 800px; }}
    
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
""", unsafe_allow_html=True)

# --- TAMPILIN HTML HEADER (DARI FILE INDEX) ---
try:
    with open("index.html", "r", encoding="utf-8") as f:
        html_header = f.read()
    
    # Bungkus pakai style biar posisinya nempel atas
    full_html = f"""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 60px; background: rgba(10,10,10,0.85); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1); z-index: 1000; display: flex; align-items: center; padding: 0 20px;">
        {html_header}
    </div>
    """
    components.html(full_html, height=60, scrolling=False)
except Exception as e:
    st.error(f"Gagal load index.html: {e}")

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
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT CHAT (PYTHON) ---
if prompt := st.chat_input("Tanya apa aja..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Ambatron sedang berpikir..."):
        response = answer(assistant, prompt, "user1")
        st.markdown(f'<div class="chat-bubble-ai">{response}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
