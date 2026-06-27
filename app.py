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

# 2. Database Initialization (For Users and Chat Logs)
def init_db():
    conn = sqlite3.connect("aryan_robot_auth.db")
    cursor = conn.cursor()
    # Table for User Credentials
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        username TEXT PRIMARY KEY, password TEXT
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

# Helper function to hash passwords for safety
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# 3. Web Layout Design & Cyber Theme
st.set_page_config(page_title="Aryan Robot Coach", page_icon="🤖", layout="wide")

# Custom CSS for UI, Animations, and Auth Portal
st.markdown("""
<style>
    .auth-container {
        max-width: 450px;
        margin: 40px auto 10px auto;
        padding: 25px;
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

# Session state control tabs
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# 🔑 AUTHENTICATION ENTRY PORTAL
if not st.session_state.logged_in:
    st.markdown("""
    <div class="auth-container">
        <h2 style="color: #38bdf8; margin-bottom: 5px;">🤖 ARYAN AI GATEWAY</h2>
        <p style="color: #94a3b8; font-size: 14px;">Sign Up naya account banane ke liye ya direct Login karein</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_action = st.tabs(["🔒 Account Login", "📝 Create Account (Sign Up)"])
    
    # 1. LOGIN TAB SECTION
    with auth_action[0]:
        col_l1, col_l2, col_l3 = st.columns([1, 3, 1])
        with col_l2:
            login_user = st.text_input("Username", key="login_u", placeholder="Enter username...")
            login_pass = st.text_input("Password", type="password", key="login_p", placeholder="Enter password...")
            
            if st.button("Access Dashboard Key 🔓", use_container_width=True):
                conn = sqlite3.connect("aryan_robot_auth.db")
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM Users WHERE username = ?", (login_user,))
                result = cursor.fetchone()
                conn.close()
                
                if result and check_hashes(login_pass, result[0]):
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error("Ghalat Username ya Password! Ek baar check karo.")
                    
    # 2
