import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd

# 1. Secure API Key Loading
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key missing in Streamlit Secrets setup. Please check Cloud Settings.")
    st.stop()

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("aryan_robot_fixed.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Voice_Logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_msg TEXT, ai_reply TEXT, mistake INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# 3. Web Layout Design & Futuristic Cyber Theme
st.set_page_config(page_title="Aryan Robot Coach", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .robot-stage {
        display: flex;
        justify-content: center;
        align-items: center;
        background: radial-gradient(circle, #0f172a 0%, #020617 100%);
        padding: 50px;
        border-radius: 20px;
        border: 2px solid #1e293b;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
        max-width: 450px;
        margin: 40px auto 10px auto;
    }
    .robot-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
    }
    .robot-box:active {
        transform: scale(0.97);
    }
    .robot-head {
        width: 110px;
        height: 90px;
        background: linear-gradient(135deg, #38bdf8 0%, #0369a1 100%);
        border-radius: 24px 24px 12px 12px;
        border: 4px solid #0f172a;
        position: relative;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 0 15px;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
        animation: floatHead 3s ease-in-out infinite;
    }
    .robot-eye {
        width: 22px;
        height: 22px;
        background-color: #00f2fe;
        border-radius: 50%;
        box-shadow: 0 0 15px #00f2fe, inset 0 0 5px #fff;
        animation: blink 4s infinite;
    }
    .robot-body-frame {
        width: 140px;
        height: 120px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 4px solid #38bdf8;
        border-radius: 18px;
        margin-top: 12px;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: inset 0 0 20px rgba(56, 189, 248, 0.2), 0 10px 20px rgba(0,0,0,0.5);
    }
    .robot-core {
        width: 50px;
        height: 50px;
        background: radial-gradient(circle, #00f2fe 0%, #4facfe 100%);
        border-radius: 50%;
        box-shadow: 0 0 25px #00f2fe;
        animation: pulseCore 1.5s alternate infinite;
    }
    @keyframes floatHead {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    @keyframes pulseCore {
        0% { transform: scale(0.9); opacity: 0.6; }
        100% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 30px #00f2fe; }
    }
    @keyframes blink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
    }
    .bot-status {
        color: #38bdf8;
        font-family: monospace;
        font-size: 14px;
        margin-top: 20px;
        letter-spacing: 2px;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Aryan AI: Interactive Touch-to-Talk Robot Coach")
st.caption("Robot ke body par direct touch/click karo aur English me baat karna shuru karo!")

# HTML Render of the Clickable Robot Body Object
st.markdown("""
<div class="robot-stage">
    <div class="robot-box" onclick="startListening()">
        <div class="robot-head">
            <div class="robot-eye"></div>
            <div class="robot-eye"></div>
        </div>
        <div class="robot-body-frame">
            <div class="robot-core"></div>
        </div>
        <div id="status-text" class="bot-status">👇 TAP MY BODY TO TALK</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Session state layer setup
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# 🎙️ HTML5 Web Speech Recognizer API Script Engine
st.markdown("""
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;

function startListening() {
    const status = document.getElementById("status-text");
    if(status) {
        status.innerHTML = "🔴 LISTENING... SPEAK NOW!";
        status.style.color = "#ef4444";
        status.style.textShadow = "0 0 10px #ef4444";
    }
    recognition.start();
}

recognition.onresult = function(event) {
    const textResult = event.results[0][0].transcript;
    parent.postMessage({type: 'streamlit:set_widget_value', id: 'voice_bridge', value: textResult}, '*');
};

recognition.onerror = function() {
    const status = document.getElementById("status-text");
    if(status) {
        status.innerHTML = "❌ TRY AGAIN: TAP HERE";
        status.style.color = "#f43f5e";
    }
};
</script>
""", unsafe_allow_html=True)

# Proxy data token bridging panel
spoken_text = st.text_input("", key="voice_bridge", label_visibility="collapsed")

# 4. Engine Core Logic Implementation
if spoken_text and spoken_text != st.session_state.voice_input:
    st.session_state.voice_input = spoken_text
    
    with st.spinner(""):
        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            prompt = f"You are Aryan AI, an English coach robot. Reply to this spoken text short and cleanly under 3 lines, then flag grammar mistakes inside brackets: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            prompt = f"Reply shortly under 3 lines and add grammar corrections: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text

    # Show Conversation Feed
    st.write("---")
    st.chat_message("user").markdown(f"**You:** {spoken_text}")
    st.chat_message("assistant").markdown(f"**Aryan Robot:** {ai_reply}")

    # 🔊 Safe Text-To-Speech String Injection (Using clean replacement logic instead of breaking f-strings)
    clean_reply = ai_reply.replace('"', '\\"').replace('\n', ' ')
    
    html_audio_script = f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{clean_reply}");
    msg.lang = 'en-US';
    msg.pitch = 0.85;
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    
    const status = document.getElementById("status-text");
    if(status) {{
        status.innerHTML = "👇 TAP MY BODY TO TALK";
        status.style.color = "#38bdf8";
        status.style.textShadow = "0 0 8px rgba(56, 189, 248, 0.6)";
    }}
    </script>
    """
    st.markdown(html_audio_script, unsafe_allow_html=True)

    # Logging Metrics
    mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
    conn = sqlite3.connect("aryan_robot_fixed.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Voice_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", (spoken_text, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
