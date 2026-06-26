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
    conn = sqlite3.connect("aryan_real_avatar.db")
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
st.set_page_config(page_title="Aryan AI Real Coach", page_icon="👔", layout="wide")

# Custom CSS for Realistic Human Coach Experience
st.markdown("""
<style>
    .real-teacher-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #111827;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.5);
        border: 2px solid #374151;
        color: white;
        text-align: center;
        max-width: 450px;
        margin: 0 auto;
    }
    .avatar-img {
        width: 220px;
        height: 220px;
        border-radius: 12px;
        object-fit: cover;
        border: 3px solid #10B981;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
    }
    .status-dot {
        height: 10px;
        width: 10px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("👔 Aryan AI: Real Human-Style Corporate English Coach")
st.caption("Aapka personal communication mentor. Mic ON kijiye aur bina hichkichahat ke baat kijiye.")

col1, col2 = st.columns([2, 1])

with col1:
    # 👨‍💼 REAL HUMAN AVATAR BODY (Using a high-quality realistic professional portrait)
    st.markdown("""
    <div class="real-teacher-card">
        <img class="avatar-img" src="https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=400" alt="Aryan AI Coach">
        <h3 style='margin-top:15px; margin-bottom:5px; color:#F9FAFB;'>Aryan AI (Senior Corporate Trainer)</h3>
        <p style='color:#9CA3AF; font-size:14px; font-style:italic;'>\"Let's practice your mock interview answers. I'm listening.\"</p>
        <div style='margin-top:10px; font-size:12px; color:#10B981; font-weight:bold;'>
            <span class="status-dot"></span>LIVE & READY TO TALK
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Analytics Panel
    st.markdown("### 📊 Live Scorecard")
    conn = sqlite3.connect("aryan_real_avatar.db")
    try:
        df = pd.read_sql_query("SELECT * FROM Voice_Logs", conn)
    except:
        df = pd.DataFrame()
    conn.close()

    if not df.empty:
        total_chats = len(df)
        total_errors = df['mistake'].sum()
        accuracy = round(((total_chats - total_errors) / total_chats) * 100, 1)
        st.metric(label="Sentences Analyzed", value=total_chats)
        st.metric(label="Fluency & Grammar Rating", value=f"{accuracy}%")
    else:
        st.info("Aapki accuracy rating yahan real-time me chalegi.")

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

st.write("---")
if st.button("🎙️ CLICK TO START SPEAKING", use_container_width=True):
    st.markdown("""<script>startListening();</script>""", unsafe_allow_html=True)
    st.warning("🔴 Aryan is listening... Speak now!")

spoken_text = st.text_input("Voice Input:", key="voice_bridge", label_visibility="collapsed")

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

    # Conversation Output Panels
    st.chat_message("user").markdown(f"**Aapne Kaha:** {spoken_text}")
    st.chat_message("assistant").markdown(f"**Aryan AI Teacher:** {ai_reply}")

    # Text-To-Speech Speaker Engine Response
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
    conn = sqlite3.connect("aryan_real_avatar.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Voice_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", (spoken_text, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
