import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd

# 1. Secure API Key Loading
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key missing in Streamlit Secrets setup.")
    st.stop()

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("aryan_robot_avatar.db")
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

# 3. Web Layout Design & Cyber Theme
st.set_page_config(page_title="Aryan Cyber Robot", page_icon="🤖", layout="wide")

# 🛠️ REAL INTERACTIVE CSS ROBOT BODY CODE
# Yeh poora custom code ek 3D stylized neon robot engine generate karta hai jo animation loop par chalta hai
st.markdown("""
<style>
    .robot-stage {
        display: flex;
        justify-content: center;
        align-items: center;
        background: radial-gradient(circle, #0f172a 0%, #020617 100%);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #1e293b;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
        max-width: 500px;
        margin: 0 auto 20px auto;
    }
    .robot-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
    }
    /* Breathing Motion Animation for Real Robot Feeling */
    .robot-head {
        width: 100px;
        height: 85px;
        background: linear-gradient(135deg, #38bdf8 0%, #0369a1 100%);
        border-radius: 20px 20px 10px 10px;
        border: 4px solid #0f172a;
        position: relative;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 0 15px;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);
        animation: floatHead 3s ease-in-out infinite;
    }
    .robot-eye {
        width: 20px;
        height: 20px;
        background-color: #00f2fe;
        border-radius: 50%;
        box-shadow: 0 0 15px #00f2fe, inset 0 0 5px #fff;
        animation: blink 4s infinite;
    }
    .robot-body-frame {
        width: 130px;
        height: 110px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 4px solid #38bdf8;
        border-radius: 15px;
        margin-top: 10px;
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        box-shadow: inset 0 0 20px rgba(56, 189, 248, 0.2), 0 10px 20px rgba(0,0,0,0.5);
    }
    .robot-core {
        width: 45px;
        height: 45px;
        background: radial-gradient(circle, #00f2fe 0%, #4facfe 100%);
        border-radius: 50%;
        box-shadow: 0 0 20px #00f2fe;
        animation: pulseCore 1.5s alternate infinite;
    }
    @keyframes floatHead {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    @keyframes pulseCore {
        0% { transform: scale(0.9); opacity: 0.6; box-shadow: 0 0 10px #00f2fe; }
        100% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 25px #00f2fe; }
    }
    @keyframes blink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
    }
    .bot-status {
        color: #38bdf8;
        font-family: monospace;
        font-size: 14px;
        margin-top: 15px;
        letter-spacing: 2px;
        text-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Aryan AI: Living Voice-to-Voice Cyber Robot")
st.caption("No images, no cartoons. Saamne active mechanical robot code engine hai. Direct bolo aur robot voice me feedback suno!")

# HTML Render of the Interactive Robot Object
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
        <div class="bot-status">🤖 ARYAN ACTIVE & LISTENING</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize Session States safely
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# 🎙️ HTML5 Voice Bridge Injection
st.markdown("""
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;

function startListening() {
    recognition.start();
}

recognition.onresult = function(event) {
    const textResult = event.results[0][0].transcript;
    parent.postMessage({type: 'streamlit:set_widget_value', id: 'voice_bridge', value: textResult}, '*');
};
</script>
""", unsafe_allow_html=True)

st.write("---")
# Primary System Activation Core Trigger
if st.button("🎤 CLICK HERE TO ACTIVATE ROBOT MIC & TALK", use_container_width=True):
    st.markdown("""<script>startListening();</script>""", unsafe_allow_html=True)
    st.info("System Triggered: Speak now into your microphone...")

spoken_text = st.text_input("Robot Input Processing:", key="voice_bridge", label_visibility="collapsed")

if spoken_text and spoken_text != st.session_state.voice_input:
    st.session_state.voice_input = spoken_text
    
    with st.spinner("Robot logic analyzing frequency metrics..."):
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

    # Console display deck
    st.chat_message("user").markdown(f"**You Spoke:** {spoken_text}")
    st.chat_message("assistant").markdown(f"**Aryan Robot:** {ai_reply}")

    # 🔊 Mechanical Robotic Voice Response
    ss_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance({repr(ai_reply)});
    msg.lang = 'en-US';
    // Tuning pitch and rate variables to produce a clean futuristic mechanical robotic sound profile
    msg.pitch = 0.8;
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(ss_code, unsafe_allow_html=True)

    # Logging Metrics
    mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
    conn = sqlite3.connect("aryan_robot_avatar.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Voice_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", (spoken_text, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
