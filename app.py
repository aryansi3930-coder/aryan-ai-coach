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

# 2. Web Layout Design & Cyber Theme
st.set_page_config(page_title="Aryan Robot Coach", page_icon="🤖", layout="wide")

# Database Engine Setup
def init_db():
    conn = sqlite3.connect("aryan_robot_final_solid.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY, 
        password TEXT,
        fullname TEXT,
        email TEXT UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Voice_Logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, user_msg TEXT, ai_reply TEXT, mistake INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

robot_css = """
<style>
    .auth-box {
        max-width: 450px;
        margin: 30px auto 10px auto;
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
        padding: 35px;
        border-radius: 20px;
        border: 2px solid #1e293b;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7);
        max-width: 450px;
        margin: 10px auto 10px auto;
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
        text-align: center;
    }
</style>
"""
st.markdown(robot_css, unsafe_allow_html=True)

# Runtime control session states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# 🔑 SECURE ISOLATED AUTH PORTAL
if not st.session_state.logged_in:
    
    # --- 1. LOGIN MODE ---
    if st.session_state.auth_mode == "login":
        st.markdown('<div class="auth-box"><h2 style="color: #38bdf8; margin-bottom: 5px;">ARYAN AI SIGN IN</h2></div>', unsafe_allow_html=True)
        
        login_input = st.text_input("Username or Email ID", key="lin_u", placeholder="Enter details").strip().lower()
        login_pass = st.text_input("Password", type="password", key="lin_p", placeholder="Enter password")
        
        if st.button("Forgot Details?", key="forgot_trigger", use_container_width=True):
            st.session_state.auth_mode = "forgot"
            st.rerun()
        
        if st.button("Unlock Session", use_container_width=True):
            if login_input == "" or login_pass == "":
                st.warning("Please fill in all fields!")
            else:
                conn = sqlite3.connect("aryan_robot_final_solid.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, fullname FROM Users WHERE (LOWER(username) = ? OR LOWER(email) = ?) AND password = ?", 
                               (login_input, login_input, login_pass))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    st.session_state.logged_in = True
                    st.session_state.current_user = result[0]
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")
        
        st.write("---")
        if st.button("Create Account (Sign Up)", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.rerun()

    # --- 2. SIGN UP MODE ---
    elif st.session_state.auth_mode == "signup":
        st.markdown('<div class="auth-box"><h2 style="color: #38bdf8; margin-bottom: 5px;">CREATE ACCOUNT</h2></div>', unsafe_allow_html=True)
        
        reg_name = st.text_input("Full Name", key="sig_n", placeholder="Your name")
        reg_email = st.text_input("Email ID", key="sig_e", placeholder="Your email").strip().lower()
        reg_user = st.text_input("Username", key="sig_u", placeholder="Unique username").strip().lower()
        reg_pass = st.text_input("Password (8-12 chars)", type="password", key="sig_p", placeholder="Create password")
        
        if st.button("Register Profile", use_container_width=True):
            if reg_name == "" or reg_email == "" or reg_user == "" or reg_pass == "":
                st.warning("All fields required!")
            elif len(reg_pass) < 8 or len(reg_pass) > 12:
                st.error("Password must be 8-12 characters!")
            elif "@" not in reg_email or "." not in reg_email:
                st.error("Invalid Email ID!")
            else:
                conn = sqlite3.connect("aryan_robot_final_solid.db")
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO Users (username, password, fullname, email) VALUES (?, ?, ?, ?)", 
                                   (reg_user, reg_pass, reg_name, reg_email))
                    conn.commit()
                    st.success("Registered successfully!")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                except sqlite3.IntegrityError as e:
                    if "email" in str(e).lower():
                        st.error("Email already registered!")
                    else:
                        st.error("Username already exists!")
                finally:
                    conn.close()
        
        st.write("---")
        if st.button("Back to Login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()

    # --- 3. RECOVERY MODE ---
    elif st.session_state.auth_mode == "forgot":
        st.markdown('<div class="auth-box"><h2 style="color: #f59e0b; margin-bottom: 5px;">RECOVER</h2></div>', unsafe_allow_html=True)
        forgot_email = st.text_input("Enter Email ID", key="for_e").strip().lower()
        
        if st.button("Recover Details", use_container_width=True):
            if forgot_email == "":
                st.warning("Please enter your email!")
            else:
                conn = sqlite3.connect("aryan_robot_final_solid.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM Users WHERE LOWER(email) = ?", (forgot_email,))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    st.success("Account Located!")
                    st.info(f"Username: {result[0]} | Password: {result[1]}")
                else:
                    st.error("Email not found in database records!")
                    
        if st.button("Back to Login", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()
    st.stop()

# 🔓 MAIN ROBOT DASHBOARD PANEL
st.title("Aryan AI: Clickable Cyber-Robot Mentor")
st.caption(f"Profile Session: {st.session_state.current_user}")

if st.sidebar.button("Log Out Securely", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.auth_mode = "login"
    st.rerun()

# Profile Analytics
st.sidebar.markdown("### Profile Analytics")
conn = sqlite3.connect("aryan_robot_final_solid.db")
try:
    df = pd.read_sql_query("SELECT * FROM Voice_Logs WHERE username = ?", conn, params=(st.session_state.current_user,))
except Exception:
    df = pd.DataFrame()
conn.close()

if not df.empty:
    total_chats = len(df)
    total_errors = df['mistake'].sum()
    accuracy = round(((total_chats - total_errors) / total_chats) * 100, 1)
    st.sidebar.metric(label="Sentences Practiced", value=total_chats)
    st.sidebar.metric(label="Grammar Accuracy", value=f"{accuracy}%")
else:
    st.sidebar.info("Use mic panel to start practice!")

# Render Robot Design
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
        <div class="bot-status">USE THE MIC PANEL BELOW TO TALK TO ME</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# 🎙️ BULLETPROOF SECURE STREAMLIT AUDIO AUDIO_INPUT PIPELINE
# Isse browser cloud permissions block nahi karega aur voice record ho jayegi
audio_file = st.audio_input("Tap microphone to record and talk:", label_visibility="visible")

if audio_file:
    with st.spinner("Processing your voice input..."):
        try:
            # Send file stream or binary chunks to Gemini multimodal audio model directly 
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            prompt = [
                "You are Aryan AI, an English coach robot. Listen to this user audio carefully. First, transcribe exactly what the user said in text, then reply shortly under 3 lines, and flag grammar mistakes inside brackets.",
                {"mime_type": "audio/wav", "data": audio_file.read()}
            ]
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception as e:
            ai_reply = "System pipeline connection busy. Please press mic and speak again."

    st.write("---")
    st.chat_message("assistant").markdown(f"**Aryan Robot:** {ai_reply}")

    # Autoplay Voice Player Synth Engine
    clean_reply = ai_reply.replace('"', '\\"').replace('\n', ' ')
    html_audio_script = f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{clean_reply}");
    msg.lang = 'en-US';
    msg.pitch = 0.85;
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(html_audio_script, unsafe_allow_html=True)

    # Permanent save inside Database file records node
    mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
    conn = sqlite3.connect("aryan_robot_final_solid.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Voice_Logs (username, user_msg, ai_reply, mistake) VALUES (?, 'Voice Audio Input', ?, ?)", 
                   (st.session_state.current_user, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
