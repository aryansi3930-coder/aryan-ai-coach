import streamlit as st
import google.generativeai as genai
import sqlite3

# 1. Secure API Key Loading
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key missing in Streamlit Secrets setup.")
    st.stop()

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("aryan_robot_clean.db")
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
st.set_page_config(page_title="Aryan Robot Coach", page_icon="🤖", layout="wide")

# Custom CSS for UI and Animations
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
        max-width: 450px;
        margin: 20px auto 10px auto;
    }
    .robot-box {
        display: flex;
        flex-direction: column;
        align-items: center;
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
    }
    @keyframes pulseCore {
        0% { transform: scale(0.9); opacity: 0.6; }
        100% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 30px #00f2fe; }
    }
    .bot-status {
        color: #38bdf8;
        font-family: monospace;
        font-size: 14px;
        margin-top: 20px;
        letter-spacing: 2px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Aryan AI: Complete Voice Robot Coach")
st.caption("No Requirements Needed! Niche diye gaye input me apna audio record karo, Robot khud bolkar reply dega.")

# Visual Robot Model
st.markdown("""
<div class="robot-stage">
    <div class="robot-box">
        <div class="robot-head">
            <div class="robot-eye"></div>
            <div class="robot-eye"></div>
        </div>
        <div class="robot-body-frame">
            <div class="robot-core"></div>
        </div>
        <div class="bot-status">🤖 ARYAN AI ONLINE</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("---")

# 🎙️ Streamlit Native Audio Input
audio_value = st.audio_input("Record your voice to talk to Aryan")

if audio_value:
    with st.spinner("Aryan is processing your voice..."):
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            audio_bytes = audio_value.read()
            
            prompt = [
                "You are Aryan AI, an English coach robot. Reply to this user audio shortly under 3 lines, then flag grammar mistakes inside brackets.",
                {"mime_type": "audio/wav", "data": audio_bytes}
            ]
            
            response = model.generate_content(prompt)
            ai_reply = response.text
            
            # Show Conversation
            st.chat_message("user").markdown("**You:** [Audio Sent]")
            st.chat_message("assistant").markdown(f"**Aryan Robot:** {ai_reply}")
            
            # 🔊 Web-Safe Text-To-Speech (Zero Libraries Required)
            clean_reply = ai_reply.replace('"', '\\"').replace('\n', ' ')
            html_audio_script = f"""
            <script>
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{clean_reply}");
            msg.lang = 'en-US';
            msg.pitch = 0.9;
            msg.rate = 1.0;
            window.speechSynthesis.speak(msg);
            </script>
            """
            st.markdown(html_audio_script, unsafe_allow_html=True)
            
            # Database Save
            mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
            conn = sqlite3.connect("aryan_robot_clean.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Voice_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", ("Audio Message", ai_reply, mistake_flag))
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")
