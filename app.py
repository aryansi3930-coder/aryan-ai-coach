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
    conn = sqlite3.connect("aryan_voice_analytics.db")
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

# 3. Web Layout Design
st.set_page_config(page_title="Aryan Voice AI Coach", page_icon="🎙️", layout="wide")
st.title("🎙️ Aryan AI: Voice English Practice Platform")
st.caption("Mic ON karo, English me baat karo, aur Aryan se bolkar feedback suno!")

# Sidebar Scorecard
st.sidebar.title("📊 Practice Scorecard")
conn = sqlite3.connect("aryan_voice_analytics.db")
df = pd.read_sql_query("SELECT * FROM Voice_Logs", conn)
conn.close()

if not df.empty:
    total_chats = len(df)
    total_errors = df['mistake'].sum()
    accuracy = round(((total_chats - total_errors) / total_chats) * 100, 1)
    st.sidebar.metric(label="Sentences Spoken", value=total_chats)
    st.sidebar.metric(label="Pronunciation/Grammar Score", value=f"{accuracy}%")
    st.sidebar.bar_chart(df['mistake'])
else:
    st.sidebar.info("Speak something to kickstart the dashboard!")

# Initialize session states
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""
if "ai_speech" not in st.session_state:
    st.session_state.ai_speech = ""

# 🛠️ JavaScript Interface for Mobile Mic & Speaker
# This injects a native HTML5 browser mic listener directly into the app frame
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

# Main Voice Trigger Button
st.subheader("Tap the button below and start speaking:")
if st.button("🎤 Click here to SPEAK (Tap to Talk)", use_container_width=True):
    st.markdown("""<script>startListening();</script>""", unsafe_allow_html=True)
    st.info("Listening to your voice... Speak now in English!")

# Bridge to catch JavaScript audio-to-text response
spoken_text = st.text_input("Transcribed Voice Output:", key="voice_bridge", label_visibility="collapsed")

# 4. Engine Processing & Audio Synthesis Loop
if spoken_text and spoken_text != st.session_state.voice_input:
    st.session_state.voice_input = spoken_text
    
    # Process with Generative Model
    with st.spinner("Aryan is listening and analyzing your accent..."):
        try:
            # Fallback model selection architecture
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            prompt = f"You are Aryan AI, an English coach. Reply to this spoken text short and cleanly under 3 lines, then flag grammar mistakes inside brackets: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
            prompt = f"Reply shortly under 3 lines and add grammar corrections: {spoken_text}"
            response = model.generate_content(prompt)
            ai_reply = response.text

    # Display Text Layout
    st.chat_message("user").markdown(f"**You Said:** {spoken_text}")
    st.chat_message("assistant").markdown(ai_reply)

    # 🔊 HTML5 Voice Output (Text-To-Speech Speaker Engine)
    # This reads back Aryan's reply directly via the user's mobile/laptop speaker safely
    ss_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance({repr(ai_reply)});
    msg.lang = 'en-US';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.markdown(ss_code, unsafe_allow_html=True)

    # Save to SQL
    mistake_flag = 1 if "mistake" in ai_reply.lower() or "wrong" in ai_reply.lower() else 0
    conn = sqlite3.connect("aryan_voice_analytics.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Voice_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", (spoken_text, ai_reply, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
