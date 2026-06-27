import streamlit as st
import google.generativeai as genai
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
    }
</style>
""", unsafe_allow_html=True)

# 🛠️ ZERO-DATABASE MEMORY SYSTEM (Bypass Crash Loop)
if "user_db" not in st.session_state:
    st.session_state.user_db = {}  # Temporary clean memory dictionary
if "chat_history_logs" not in st.session_state:
    st.session_state.chat_history_logs = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# 🔑 ULTRA-STABLE AUTH PORTAL
if not st.session_state.logged_in:
    
    # --- 1. LOGIN MODE ---
    if st.session_state.auth_mode == "login":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #38bdf8; margin-bottom: 5px;">🤖 ARYAN AI SIGN IN</h2>
            <p style="color: #94a3b8; font-size: 14px;">Username ya Email ID daal kar login karein</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_input = st.text_input("Username or Email ID", key="lin_u", placeholder="Enter username or email...").strip().lower()
            login_pass = st.text_input("Password", type="password", key="lin_p", placeholder="Enter password...")
            
            if st.button("Forgot Account details? 🔍", key="forgot_trigger"):
                st.session_state.auth_mode = "forgot"
                st.rerun()
            
            if st.button("Unlock Session 🔓", use_container_width=True):
                if login_input == "" or login_pass == "":
                    st.warning("Please fill in all fields!")
                else:
                    # Check in memory database loop
                    user_found = None
                    for u, data in st.session_state.user_db.items():
                        if (u == login_input or data["email"] == login_input) and data["password"] == login_pass:
                            user_found = u
                            break
                    
                    if user_found:
                        st.session_state.logged_in = True
                        st.session_state.current_user = st.session_state.user_db[user_found]["fullname"]
                        st.success(f"Access Granted!")
                        st.rerun()
                    else:
                        st.error("Invalid Username, Email or Password!")
            
            st.write("---")
            if st.button("Create an Account (Sign Up) 📝", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

    # --- 2. SIGN UP MODE ---
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
            reg_email = st.text_input("Email ID", key="sig_e", placeholder="Enter your email address...").strip().lower()
            reg_user = st.text_input("Choose Username", key="sig_u", placeholder="Create unique username...").strip().lower()
            reg_pass = st.text_input("Choose Password (8-12 chars)", type="password", key="sig_p", placeholder="Create password...")
            
            if st.button("Register & Save Profile 🚀", use_container_width=True):
                # Unique Email verification check
                email_exists = any(data["email"] == reg_email for data in st.session_state.user_db.values())
                
                if reg_name == "" or reg_email == "" or reg_user == "" or reg_pass == "":
                    st.warning("Saari fields bharna zaroori hai!")
                elif len(reg_pass) < 8 or len(reg_pass) > 12:
                    st.error(f"Password Strictly 8 se 12 digits ka hona chahiye (Aapka password {len(reg_pass)} digits ka hai).")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid Email ID!")
                elif reg_user in st.session_state.user_db:
                    st.error("Username already exists! Try another one.")
                elif email_exists:
                    st.error("Yeh Email ID pehle se registered hai!")
                else:
                    # Save natively in active instance cache dictionary node
                    st.session_state.user_db[reg_user] = {
                        "password": reg_pass,
                        "fullname": reg_name,
                        "email": reg_email
                    }
                    st.success("Account registered successfully!")
                    st.session_state.auth_mode = "login"
                    st.rerun()
            
            st.write("---")
            if st.button("Back to Login 🔒", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

    # --- 3. RECOVERY MODE ---
    elif st.session_state.auth_mode == "forgot":
        st.markdown("""
        <div class="auth-box">
            <h2 style="color: #f59e0b; margin-bottom: 5px;">🔍 RECOVER ACCOUNT</h2>
            <p style="color: #94a3b8; font-size: 14px;">Registered Email daalkar username dhoondhein</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            forgot_email = st.text_input("Enter Registered Email ID", key="for_e").strip().lower()
            
            if st.button("Recover Details 🛠️", use_container_width=True):
                user_found = None
                for u, data in st.session_state.user_db.items():
                    if data["email"] == forgot_email:
                        user_found = u
                        break
                
                if user_found:
                    st.success(f"Account Located!")
                    st.info(f"👉 **Your Username:** `{user_found}`")
                else:
                    st.error("Yeh Email ID memory me nahi mili!")
                        
            if st.button("Back to Login 🔒", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
    st.stop()

# 🔓 MAIN ROBOT DASHBOARD PANEL
st.title("🤖 Aryan AI: Clickable Cyber-Robot Mentor")
st.caption(f"Profile Session: 👤 {st.session_state.current_user}")

# Sidebar config
if st.sidebar.button("Log Out Securely 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.auth_mode = "login"
    st.rerun()

# Sidebar analytics calculator using memory metrics list
st.sidebar.markdown(f"### 📊 Profile Analytics")
total_chats = len(st.session_state.chat_history_logs)
if total_chats > 0:
    total_errors = sum(1 for
