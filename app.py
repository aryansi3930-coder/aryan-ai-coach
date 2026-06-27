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

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("aryan_robot_auth_v4.db")
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

# Helper functions for Password Security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 3. Web Layout Design & Cyber Theme
st.set_page_config(page_title="Aryan Robot Coach", page_icon="🤖", layout="wide")

# Custom CSS for Mechanical Robot Body & UI Animations
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

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# 🔑 LOGIN / SIGN UP SECURITY PORTAL
if not st.session_state.logged_in:
    
    if st.session_state.auth_mode == "login":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #38bdf8; margin-bottom: 5px;">🤖 ARYAN AI SIGN IN</h2>
            <p style="color: #94a3b8; font-size: 14px;">Username ya Email ID daal kar login karein</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_input = st.text_input("Username or Email ID", key="lin_u", placeholder="Enter username or email...").strip()
            login_pass = st.text_input("Password", type="password", key="lin_p", placeholder="Enter password...")
            
            if st.button("Forgot Account details? 🔍", key="forgot_trigger"):
                st.session_state.auth_mode = "forgot"
                st.rerun()
            
            if st.button("Unlock Session 🔓", use_container_width=True):
                if login_input == "" or login_pass == "":
                    st.warning("Please fill in all fields!")
                else:
                    hashed_login_pass = make_hashes(login_pass)
                    conn = sqlite3.connect("aryan_robot_auth_v4.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT username FROM Users WHERE (username = ? OR email = ?) AND password = ?", 
                                   (login_input, login_input, hashed_login_pass))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        st.session_state.logged_in = True
                        st.session_state.current_user = result[0]
                        st.success(f"Access Granted!")
                        st.rerun()
                    else:
                        st.error("Invalid Credentials!")
            
            st.write("---")
            if st.button("Create an Account (Sign Up) 📝", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

    elif st.session_state.auth_mode == "signup":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #38bdf8; margin-bottom: 5px;">📝 CREATE NEW ACCOUNT</h2>
            <p style="color: #94a3b8; font-size: 14px;">Password criteria: 8 to 12 characters only</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            reg_name = st.text_input("Full Name", key="sig_n", placeholder="Enter your full name...")
            reg_email = st.text_input("Email ID", key="sig_e", placeholder="Enter your email address...").strip()
            reg_user = st.text_input("Choose Username", key="sig_u", placeholder="Create unique username...").strip()
            reg_pass = st.text_input("Choose Password (8-12 chars)", type="password", key="sig_p", placeholder="Create password...")
            
            if st.button("Register & Save Profile 🚀", use_container_width=True):
                if reg_name == "" or reg_email == "" or reg_user == "" or reg_pass == "":
                    st.warning("Saari fields bharna zaroori hai!")
                elif len(reg_pass) < 8 or len(reg_pass) > 12:
                    st.error("Password strictly 8 se 12 digits ke beech hona chahiye.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid Email ID!")
                else:
                    hashed_password = make_hashes(reg_pass)
                    conn = sqlite3.connect("aryan_robot_auth_v4.db")
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO Users (username, password, fullname, email) VALUES (?,?,?,?)", 
                                       (reg_user, hashed_password, reg_name, reg_email))
                        conn.commit()
                        st.success("Account registered!")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    except sqlite3.IntegrityError as e:
                        if "email" in str(e).lower():
                            st.error("Yeh Email ID pehle se registered hai!")
                        else:
                            st.error("Username already exists!")
                    finally:
                        conn.close()
            
            st.write("---")
            if st.button("Back to Login 🔒", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

    elif st.session_state.auth_mode == "forgot":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #f59e0b; margin-bottom: 5px;">🔍 RECOVER ACCOUNT</h2>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            forgot_email = st.text_input("Enter Registered Email ID", key="for_e").strip()
            if st.button("Recover Details 🛠️", use_container_width=True):
                conn = sqlite3.connect("aryan_robot_auth_v4.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, fullname FROM Users WHERE email = ?", (forgot_email,))
                result = cursor.fetchone()
                conn.close()
                if result:
                    st.success(f"Hello {result[1]}! Your Username is: `{result[0]}`")
                else:
                    st.error("Email not found!")
            if st.button("Back to Login 🔒", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
    st.stop()

# 🔓 MAIN SYSTEM DASHBOARD (VISIBLE AFTER LOGIN)
st.title("🤖 Aryan AI: Clickable Cyber-Robot Mentor")
st.caption(f"Profile: Active Session 👤 {st.session_state.current_user}")

# Sidebar configurations
if st.sidebar.button("Log Out Securely 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.auth_mode = "login"
    st.rerun()

# Sidebar Track panel
st.sidebar.markdown(f"### 📊 Profile Analytics")
conn = sqlite3.connect("aryan_robot_auth_v4.db")
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
    st.sidebar.info("Tap robot and talk to start analytics profiles!")

# 🤖 CLICKABLE MECHANICAL ROBOT COMPONENT (Direct Tap Activation)
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

# 🎙️ Bridge Pipeline Javascript Engine 
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

# Hidden pipeline tracking token input
spoken_text = st.text_input("", key="voice_bridge", label_visibility="collapsed")

# 4. Processing Robot Response
if spoken_text and spoken_text != st.session_state.voice_input:
    st.session_state.voice_input = spoken_text
    
    with st.spinner(""):
        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            prompt = f"You are Aryan AI, an English coach robot. Reply to this spoken text short and cleanly under 3 lines, then flag grammar mistakes inside brackets: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception:
            ai_reply = "Connection unstable. Please tap my body and speak again."

    # Show Conversation
    st.write("---")
    st.chat_message("user").markdown(f"**You:** {spoken_text}")
    st.chat_message("assistant").markdown(f"**Aryan Robot:** {ai_reply}")

    # 🔊 Autoplay Text-To-Speech Injection Script
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

    # Metrics Logging
    mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
    conn = sqlite3.connect("aryan_robot_auth_v4.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Voice_Logs (username, user_msg, ai_reply, mistake) VALUES (?, ?, ?, ?)", 
                   (st.session_state.current_user, spoken_text, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
