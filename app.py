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

# ZERO-DATABASE MEMORY SYSTEM
if "user_db" not in st.session_state:
    st.session_state.user_db = {}  
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

# 🔑 AUTHENTICATION FLOW PORTAL
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
            reg_email = st.text_input("
