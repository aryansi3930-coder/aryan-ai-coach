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

# Database Connection Setup
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
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO Users (username, password, fullname, email) 
            VALUES ('aryan', '12345678', 'Aryan Singh', 'aryan@test.com')
        """)
        conn.commit()
    except Exception:
        pass
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
        border-left: 5px solid #f43f5e;
        margin-top: 15px;
        color: white;
    }
</style>
"""
st.markdown(robot_css, unsafe_allow_html=True)

# Runtime session state components
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# 🔑 SECURE AUTHENTICATION CONTAINER
if not st.session_state.logged_in:
    if st.session_state.auth_mode == "login":
        st.markdown('<div class="auth-box"><h2 style="color: #38bdf8; margin-bottom: 5px;">ARYAN AI SIGN IN</h2></div>', unsafe_allow_html=True)
        login_input = st.text_input("Username or Email ID", key="lin_u", placeholder="Enter username or email...").strip().lower()
        login_pass = st.text_input("Password", type="password", key="lin_p", placeholder="Enter password...")
        
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
        reg_pass = st.text_input("Password (8-12 chars)", type="password", key="sig_p", placeholder="Create password")
        
        if st.button("Register Profile", use_container_width=True):
            if reg_name == "" or reg_email == "" or reg_user == "" or reg_pass == "":
                st.warning("All fields required!")
            elif len(reg_pass) < 8 or len(reg_pass) > 12:
                st.error("Password must be 8-12 characters!")
            elif "@" not in reg_email or "." not in reg_email:
                st.error("Invalid Email ID!")
            else:
                conn = sqlite3.connect("aryan_robot_master_v5.db")
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

    elif st.session_state.auth_mode == "forgot":
        st.markdown('<div class="auth-box"><h2 style="color: #f59e0b; margin-bottom: 5px;">RECOVER</h2></div>', unsafe_allow_html=True)
        forgot_email = st.text_input("Enter Email ID", key="for_e", placeholder="Enter registered email...").strip().lower()
        if st.button("Recover Details", use_container_width=True):
            if forgot_email == "":
                st.warning("Please enter your email!")
            else:
                conn = sqlite3.connect("aryan_robot_master_v5.db")
                cursor = conn.cursor()
                cursor.execute("SELECT username, password FROM Users WHERE LOWER(email) = ?", (forgot_email,))
                result = cursor.fetchone()
                conn.close()
                if result:
                    st.success("Account Located!")
                    st.info("Username: {} | Password: {}".format(result[0], result[1]))
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

# Profile Analytics Dashboard Sidebar
st.sidebar.markdown("### Profile Analytics")
conn = sqlite3.connect("aryan_robot_master_v5.db")
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
        <div class="bot-status">TALK TO ME BELOW</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# 🎙️ AUDIO INPUT PANEL
audio_file = st.audio_input("Tap microphone to record and talk:", label_visibility="visible")

if audio_file:
    # Set default structures in case API drops or limit hits
    transcribed = "Audio Processed"
    corrected = "Perfect"
    reason = "None"
    hindi = ""
    reply = "Great talking to you!"
    mistake_val = 0
    save_to_db = True

    with st.spinner("Analyzing audio content and grammar logic..."):
        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            
            prompt = [
                """You are Aryan AI, a professional English voice coach. Listen to this user audio carefully.
                You must process the audio and provide the output EXACTLY in this format. Do not use markdown bold inside fields, separate lines by pipes (|).
                Format structure:
                Transcribed: [Exact text what user said in audio]
                Corrected: [If mistake, write the grammatically correct version. If 100% correct, write "Perfect"]
                Reason: [If mistake, explain the grammar rule in clear simple Hinglish. If correct, write "None"]
                Hindi: [Hindi translation of what user said in English using Hindi script]
                Reply: [Your short smart mentor reply under 2 lines in English]
                Mistake_Flag: [Write 1 if user made a grammar/pronunciation mistake, write 0 if user was 100% correct]
                """,
                {"mime_type": "audio/wav", "data": audio_file.read()}
            ]
            response = model.generate_content(prompt)
            raw_response = response.text

            lines = raw_response.split("\n")
            for line in lines:
                if "Transcribed:" in line: transcribed = line.split("Transcribed:")[1].strip()
                if "Corrected:" in line: corrected = line.split("Corrected:")[1].strip()
                if "Reason:" in line: reason = line.split("Reason:")[1].strip()
                if "Hindi:" in line: hindi = line.split("Hindi:")[1].strip()
                if "Reply:" in line: reply = line.split("Reply:")[1].strip()
                if "Mistake_Flag:" in line: 
                    try:
                        mistake_val = int(line.split("Mistake_Flag:")[1].strip())
                    except:
                        mistake_val = 1 if "1" in line else 0

        # 🎯 MASTER FIX: Catch Google Quota Limits safely
        except Exception as e:
            save_to_db = False  # Limit leak block fallback
            transcribed = "Mic transmission busy"
            corrected = "Connection Tier Reset"
            hindi = "गूगल सर्वर अभी व्यस्त है"
            
            if "429" in str(e) or "quota" in str(e).lower():
                reply = "Google AI free limit reached. Please wait 30-50 seconds and tap mic again!"
                reason = "Google API has a strict 15 requests per minute limit on free keys."
            else:
                reply = "Connection unstable. Let's try again."
                reason = str(e)

    # 🔓 UI FEEDBACK INTERFACE DISPLAYERS
    st.write("---")
    st.markdown("### 🎙️ Session Feedback Analysis")
    
    col_u, col_r = st.columns(2)
    with col_u:
        st.chat_message("user").markdown(f"**What You Said:** {transcribed}")
        if hindi:
            st.caption(f"🇮🇳 *Hindi Meaning:* {hindi}")
            
    with col_r:
        st.chat_message("assistant").markdown(f"**Aryan Robot:** {reply}")
        
    # Display Card engine
    if not save_to_db:
        st.error(reply)
    elif mistake_val == 1 or (corrected.lower() != "perfect" and corrected != ""):
        card_html = '<div class="feedback-card"><h4 style="color: #f43f5e; margin:0 0 5px 0;">⚠️ Grammar Correction Required:</h4><p style="color: #e2e8f0; margin:0 0 5px 0;"><b>Sahi Answer:</b> {}</p><p style="color: #94a3b8; margin:0;"><b>Reason (Kyun?):</b> {}</p></div>'.format(corrected, reason)
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.success("Excellent! Your sentence structure was 100% correct. Keep it up!")

    # 🔊 Autoplay Voice Player Synth Engine
    clean_reply = reply.replace('"', '\\"').replace('\n', ' ')
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

    # 💾 SAVE DATA TO PERMANENT SQLite DB STORAGE (Only if API request was healthy)
    if save_to_db:
        conn = sqlite3.connect("aryan_robot_master_v5.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Voice_Logs (username, user_msg, correct_msg, reason, hindi_trans, ai_reply, mistake) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (st.session_state.current_user, transcribed, corrected, reason, hindi, reply, mistake_val))
        conn.commit()
        conn.close()
        st.rerun()
