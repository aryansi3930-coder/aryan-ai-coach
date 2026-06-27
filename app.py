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

# 🗄️ MASTER FIX: Changed database name to v5 to force SQLite to create the new column structure
def init_db():
    conn = sqlite3.connect("aryan_robot_master_v5.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY, 
        password TEXT,
        fullname TEXT,
        email TEXT UNIQUE
    )
    """)
    # Table explicitly containing all 8 operational schema nodes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Voice_Logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, 
        user_msg TEXT, 
        correct_msg TEXT,
        reason TEXT,
        hindi_trans TEXT,
        ai_reply TEXT, 
        mistake INTEGER
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
    .feedback-card {
        background: #0f172a;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #38bdf8;
        margin-top: 15px;
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
                conn = sqlite3.connect("aryan_robot_master_v5.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM Users WHERE (LOWER(username) = ? OR LOWER(email) = ?) AND password = ?", 
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

    elif st.session_state.auth_mode == "signup":
        st.markdown('<div class="auth-box"><h2 style="color: #38bdf8; margin-bottom: 5px;">CREATE ACCOUNT</h2></div>', unsafe_allow_html=True)
        reg_name = st.text_input("Full Name", key="sig_n", placeholder="Your name")
        reg_email = st.text_input("Email ID", key="sig_e", placeholder="Your email").strip().lower()
        reg_user = st.text_input("Username", key="sig_u", placeholder="Unique username").strip().lower()
        reg_pass = st.text_input("Password (8-12 chars)", type
