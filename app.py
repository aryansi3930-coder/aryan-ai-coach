import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib
import pandas as pd

# 1. Secure API Key Loading
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key missing in Streamlit Secrets setup.")
    st.stop()

# 2. Database Initialization (Fixed Table Setup)
def init_db():
    conn = sqlite3.connect("aryan_robot_auth_v3.db")
    cursor = conn.cursor()
    # Table for User Profiles and Credentials
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY, 
        password TEXT,
        fullname TEXT,
        email TEXT
    )
    """)
    # Table for Robot Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Voice_Logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, user_msg TEXT, ai_reply TEXT, mistake INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper functions for Password Security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 3. Web Layout Design & Cyber Theme
st.set_page_config(page_title="Aryan Robot Coach", page_icon="🤖", layout="wide")

# Custom CSS for Professional UI Layout
st.markdown("""
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

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# 🔑 SINGLE CONTAINER SYSTEM (LOGIN & SIGNUP TOGGLE)
if not st.session_state.logged_in:
    
    if st.session_state.auth_mode == "login":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #38bdf8; margin-bottom: 5px;">🤖 ARYAN AI SIGN IN</h2>
            <p style="color: #94a3b8; font-size: 14px;">Enter credentials to unlock your coach</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_user = st.text_input("Username", key="lin_u", placeholder="Enter username...").strip()
            login_pass = st.text_input("Password", type="password", key="lin_p", placeholder="Enter password...")
            
            if st.button("Unlock Session 🔓", use_container_width=True):
                if login_user == "" or login_pass == "":
                    st.warning("Please fill in both fields!")
                else:
                    hashed_login_pass = make_hashes(login_pass)
                    conn = sqlite3.connect("aryan_robot_auth_v3.db")
                    cursor = conn.cursor()
                    # 🎯 FIXED LOGIC: Match user credentials against hashed strings natively
                    cursor.execute("SELECT username FROM Users WHERE username = ? AND password = ?", (login_user, hashed_login_pass))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        st.session_state.logged_in = True
                        st.session_state.current_user = result[0]
                        st.success(f"Access Granted! Welcome back.")
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password! Double check your credentials.")
            
            st.write("---")
            st.write("Don't have an account yet?")
            if st.button("Create an Account (Sign Up) 📝", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

    elif st.session_state.auth_mode == "signup":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #38bdf8; margin-bottom: 5px;">📝 CREATE NEW ACCOUNT</h2>
            <p style="color: #94a3b8; font-size: 14px;">Fill details to register on Robot Database</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            reg_name = st.text_input("Full Name", key="sig_n", placeholder="Enter your full name...")
            reg_email = st.text_input("Email ID", key="sig_e", placeholder="Enter your email address...")
            reg_user = st.text_input("Choose Username", key="sig_u", placeholder="Create unique username...").strip()
            reg_pass = st.text_input("Choose Password", type="password", key="sig_p", placeholder="Create strong password...")
            
            if st.button("Register & Save Profile 🚀", use_container_width=True):
                if reg_name == "" or reg_email == "" or reg_user == "" or reg_pass == "":
                    st.warning("Saari fields bharna zaroori hai!")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid Email ID!")
                else:
                    hashed_password = make_hashes(reg_pass)
                    conn = sqlite3.connect("aryan_robot_auth_v3.db")
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO Users (username, password, fullname, email) VALUES (?,?,?,?)", 
                                       (reg_user, hashed_password, reg_name, reg_email))
                        conn.commit()
                        st.success("Account successfully registered! Proceeding to Sign In...")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists! Try another one.")
                    finally:
                        conn.close()
            
            st.write("---")
            st.write("Already have an account?")
            if st.button("Back to Login 🔒", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
                
    st.stop()

# 🔓 MAIN SYSTEM DASHBOARD (Accessible only after login)
st.title("🤖 Aryan AI: Complete Voice Robot Coach")
st.caption(f"Active User Profile: 👤 {st.session_state.current_user}")

# Sidebar adjustments
if st.sidebar.button("Log Out Securely 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.auth_mode = "login"
    st.rerun()

# Dynamic metric engine logs
st.sidebar.markdown(f"### 📊 Track Profile")
conn = sqlite3.connect("aryan_robot_auth_v3.db")
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
    st.sidebar.info("Start speaking to populate analytics panels!")

# Robot UI Render Frame
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
            
            # Show Conversation Feed
            st.chat_message("user").markdown("**You:** [Audio Sent]")
            st.chat_message("assistant").markdown(f"**Aryan Robot:** {ai_reply}")
            
            # 🔊 Web-Safe Text-To-Speech Engine
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
            
            # Database Save linked specifically to the current user
            mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
            conn = sqlite3.connect("aryan_robot_auth_v3.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Voice_Logs (username, user_msg, ai_reply, mistake) VALUES (?, ?, ?, ?)", 
                           (st.session_state.current_user, "Audio Message", ai_reply, mistake_flag))
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")
