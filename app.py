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

# Custom CSS for UI, Animations, and Login Screen
st.markdown("""
<style>
    /* Styling for Login Box */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 30px;
        background: #1e293b;
        border-radius: 15px;
        border: 2px solid #38bdf8;
        box-shadow: 0 10px 30px rgba(56, 189, 248, 0.2);
        text-align: center;
        color: white;
    }
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
    }
</style>
""", unsafe_allow_html=True)

# 🔑 LOGIN SYSTEM LOGIC
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Login Window UI
    st.markdown("""
    <div class="login-container">
        <h2 style="color: #38bdf8; margin-bottom: 5px;">🤖 ARYAN AI GATEWAY</h2>
        <p style="color: #94a3b8; font-size: 14px;">Please login to access your AI Coach</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Forms inside container using Streamlit columns for spacing
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        username = st.text_input("Username", placeholder="Enter username...")
        password = st.text_input("Password", type="password", placeholder="Enter password...")
        
        # 🎯 Credential Check: Username = admin, Password = admin123 (Inhe badal sakte ho)
        if st.button("Secure Login 🔒", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.success("Login Successful! Access Granted.")
                st.rerun()
            else:
                st.error("Invalid Username or Password! Access Denied.")
    st.stop() # Stops execution here so robot screen doesn't render without login

# 🔓 MAIN APPLICATION CONTAINER (Will only open if logged_in is True)
st.title("🤖 Aryan AI: Complete Voice Robot Coach")
st.caption("Access Status: SECURE CLIENT SESSION 🟢")

# Logout button inside sidebar
if st.sidebar.button("Log Out 🚪"):
    st.session_state.logged_in = False
    st.rerun()

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
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
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
            
            # 🔊 Web-Safe Text-To-Speech
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
