import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd

# 1. API Configuration
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("API Key missing in Streamlit Secrets setup.")
    st.stop()

# 2. Database Initialization
def init_db():
    conn = sqlite3.connect("aryan_web_analytics.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Web_Logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_msg TEXT, ai_reply TEXT, mistake INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# 3. AI Model Setup (Foolproof Model Fallback)
SYSTEM_INSTRUCTION = """
You are 'Aryan AI', an elite corporate English communication coach. Talk professionally and guide the user like a mentor.
At the end of your response, ALWAYS provide this exact structured section:
---
[GRAMMAR CHECK]: Point out mistakes and give corrected version. If none, say "Perfect Grammar!".
[SMARTER VOCABULARY]: Suggest 2 advanced business words for their sentence.
"""

# Dynamic model handling to bypass any version issues
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction=SYSTEM_INSTRUCTION
    )
except Exception:
    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-flash", 
        system_instruction=SYSTEM_INSTRUCTION
    )

# 4. Streamlit Web UI Layout Design
st.set_page_config(page_title="Aryan AI Coach", page_icon="🎯", layout="wide")

st.title("🎯 Aryan AI: Professional English Practice Platform")
st.caption("Welcome! I am Aryan, your personal AI Coach. Let's sharpen your corporate communication skills together.")

# Sidebar for Analytics Dashboard
st.sidebar.title("📊 Aryan's Analytics Board")
conn = sqlite3.connect("aryan_web_analytics.db")
df = pd.read_sql_query("SELECT * FROM Web_Logs", conn)
conn.close()

if not df.empty:
    total_chats = len(df)
    total_errors = df['mistake'].sum()
    accuracy = round(((total_chats - total_errors) / total_chats) * 100, 1)
    
    st.sidebar.metric(label="Total Sentences Practiced", value=total_chats)
    st.sidebar.metric(label="Grammar Accuracy Score", value=f"{accuracy}%")
    
    st.sidebar.subheader("Your Progress Trend")
    st.sidebar.bar_chart(df['mistake'])
else:
    st.sidebar.info("Start chatting to activate your dashboard tracker!")

# Chat Interface Setup
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["text"])

if user_input := st.chat_input("Type your English sentence here..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("Aryan is analyzing your sentence structure..."):
            try:
                # Direct generate content loop to avoid session crashes
                response = model.generate_content(user_input)
                ai_response_text = response.text
                st.markdown(ai_response_text)
            except Exception as api_err:
                st.error(f"AI Service Error: {api_err}. Please ensure your API key in Secrets is completely correct.")
                st.stop()
            
    st.session_state.chat_history.append({"role": "assistant", "text": ai_response_text})
    
    mistake_flag = 1 if "[GRAMMAR CHECK]" in ai_response_text and "Perfect Grammar!" not in ai_response_text else 0
    conn = sqlite3.connect("aryan_web_analytics.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Web_Logs (user_msg, ai_reply, mistake) VALUES (?, ?, ?)", (user_input, ai_response_text, mistake_flag))
    conn.commit()
    conn.close()
    
    st.rerun()
