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

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("aryan_voice_avatar.db")
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

# 3. Web Layout Design & Theme
st.set_page_config(page_title="Aryan AI Voice Teacher", page_icon="👨‍🏫", layout="wide")

# Custom CSS for the AI Teacher's Body and Visual Feeling
st.markdown("""
<style>
    .teacher-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.3);
        margin-bottom: 25px;
        color: white;
        text-align: center;
    }
    .avatar-body {
        width: 140px;
        height: 140px;
        background-color: #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 75px;
        border: 5px solid #00d2ff;
        box-shadow: 0 0 20px #00d2ff;
        animation: float 3s ease-in-out infinite;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    .status-badge {
        background-color: #00d2ff;
        color: #1e3c72;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        margin-top: 15px;
        font-size: 14px;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Aryan AI: Interactive Voice English Teacher")
st.caption("Ab rona-dhona band! Saamne aapka digital corporate mentor khada hai. Mic dabaao aur baatein shuru karo.")

# Layout splitting: Left for Avatar Teacher, Right for Analytics Scorecard
col1, col2 = st.columns([2, 1])

with col1:
    # 👨‍🏫 THE AI TEACHER'S PHYSICAL FRAME BODY
    st.markdown("""
    <div class="teacher-container">
        <div class="avatar-body">👨‍💼</div>
        <h2 style='margin-top:10px; color:white;'>Aryan AI Coach</h2>
        <p style='color:#e0e0e0; font-style: italic;'>\"I am listening to your sentence structure. Speak naturally!\"</p>
        <div class="status-badge">ONLINE & READY</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Sidebar / Analytics Panel
    st.markdown("### 📊 Performance Analytics")
    conn = sqlite3.connect("aryan_web_analytics.db")
    try:
        df = pd.read_sql_query("SELECT * FROM Web_Logs", conn)
    except:
        df = pd.DataFrame()
    conn.close()

    if not df.empty:
        total_chats = len(df)
        total_errors = df['mistake'].sum()
        accuracy = round(((total_chats - total_errors) / total_chats) * 100, 1)
        st.metric(label="Sentences Practiced", value=total_chats)
        st.metric(label="Communication Accuracy Score", value=f"{accuracy}%")
    else:
        st.info("Speak to activate metrics card!")

# Initialize session states
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# JavaScript Browser Audio Interface
st.markdown("""
<script>
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;

function startListening() {
    recognition.start();
}

recognition.onresult = function(event) {
    const textResult = event.results[0][0].transcript;
    parent.postMessage({type: 'streamlit:set_widget_value', id: 'voice_bridge', value: textResult}, '*');
};
</script>
""", unsafe_allow_html=True)

# Audio Control Hub
st.write("---")
if st.button("🎙️ TAP TO TALK (Speak Now)", use_container_width=True):
    st.markdown("""<script>startListening();</script>""", unsafe_allow_html=True)
    st.warning("🔴 Aryan is listening to your speech... Say something in English!")

# Dynamic voice data ingestion deck
spoken_text = st.text_input("Voice Token Output:", key="voice_bridge", label_visibility="collapsed")

if spoken_text and spoken_text != st.session_state.voice_input:
    st.session_state.voice_input = spoken_text
    
    with st.spinner("Aryan is evaluating your grammar style..."):
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            prompt = f"You are Aryan AI, an English coach. Reply to this spoken text short and cleanly under 3 lines, then flag grammar mistakes inside brackets: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception:
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
            prompt = f"Reply shortly under 3 lines and add grammar corrections: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text

    # Show conversational layout
    st.chat_message("user").markdown(f"**You:** {spoken_text}")
    st.chat_message("assistant").markdown(f"**Aryan AI Teacher:** {ai_reply}")

    # 🔊 Real-time Speech Synth Engine Response
    ss_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance({repr(ai_reply)});
    msg.lang = 'en-US';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(ss_code, unsafe_allow_html=True)

    # Database Commits
    mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
    conn = sqlite3.connect("aryan_web_analytics.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Web_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", (spoken_text, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
