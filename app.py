import streamlit as st
import google.generativeai as genai
import sqlite3
import hashlib

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
    
    # Login vs Sign Up Menu Tabs
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
                    
    # 2. SIGN UP TAB SECTION
    with auth_action[1]:
        col_s1, col_s2, col_s3 = st.columns([1, 3, 1])
        with col_s2:
            new_user = st.text_input("Choose Username", key="sign_u", placeholder="Create unique username...")
            new_pass = st.text_input("Choose Password", type="password", key="sign_p", placeholder="Create strong password...")
            confirm_pass = st.text_input("Confirm Password", type="password", key="sign_cp", placeholder="Re-type password...")
            
            if st.button("Register Account 🚀", use_container_width=True):
                if new_user == "" or new_pass == "":
                    st.warning("Username aur Password fields khali nahi ho sakti!")
                elif new_pass != confirm_pass:
                    st.error("Passwords match nahi ho rahe hain! Dubara type karo.")
                else:
                    hashed_password = make_hashes(new_pass)
                    conn = sqlite3.connect("aryan_robot_auth.db")
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO Users (username, password) VALUES (?,?)", (new_user, hashed_password))
                        conn.commit()
                        st.success("Account successfully created! Ab upar 'Account Login' tab par jaakar login karo.")
                    except sqlite3.IntegrityError:
                        st.error("Yeh Username pehle se kisi ne le rakha hai! Kuch alag try karo.")
                    finally:
                        conn.close()
    st.stop()

# 🔓 MAIN SYSTEM DASHBOARD (Only visible post-login validation)
st.title("🤖 Aryan AI: Complete Voice Robot Coach")
st.caption(f"Secure Session Profile: Active User 👤 {st.session_state.current_user}")

# Sidebar configurations
if st.sidebar.button("Log Out Securely 🚪", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.rerun()

# Dashboard scorecard logic specific to the logged-in user
st.sidebar.markdown(f"### 📊 {st.session_state.current_user}'s Progress")
conn = sqlite3.connect("aryan_robot_auth.db")
df = pd.read_sql_query("SELECT * FROM Voice_Logs WHERE username = ?", conn, params=(st.session_state.current_user,))
conn.close()

if not df.empty:
    total_chats = len(df)
    total_errors = df['mistake'].sum()
    accuracy = round(((total_chats - total_errors) / total_chats) * 100, 1)
    st.sidebar.metric(label="Sentences Practiced", value=total_chats)
    st.sidebar.metric(label="Grammar Accuracy Score", value=f"{accuracy}%")
else:
    st.sidebar.info("Start speaking to record metrics profile!")

# Visual Robot Model Frame
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
