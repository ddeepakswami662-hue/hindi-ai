import sqlite3
import streamlit as st
from groq import Groq
from streamlit_mic_recorder import mic_recorder

st.title("🤖 Hindi AI Chat Bot (History + Photo + Mic)")

# Streamlit secrets se API key uthana
if "GROQ_API_KEY" in st.secrets:
  client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
  st.error("Groq API Key missing! Please configure it in Streamlit Secrets.")
  st.stop()


# --- DATABASE SETUP (Permanent History) ---
def init_db():
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
  conn.commit()
  return conn, cursor


conn, cursor = init_db()

# Database se purani messages load karna
cursor.execute("SELECT role, content FROM messages")
db_messages = cursor.fetchall()

if "messages" not in st.session_state:
  st.session_state.messages = []
  for role, content in db_messages:
    st.session_state.messages.append({"role": role, "content": content})


# --- SIDEBAR: PHOTO & MIC INPUT ---
with st.sidebar:
  st.header("⚙️ Media & Voice")

  # 1. Photo Upload
  uploaded_file = st.file_uploader(
      "Photo upload karein:", type=["jpg", "jpeg", "png"]
  )
  if uploaded_file is not None:
    st.success("Photo upload ho gayi!")

  st.markdown("---")
  st.subheader("🎙️ Voice Input")
  st.write("Bol kar message bhejne ke liye mic dabayein:")

  # 2. Mic Recorder Button (Streamlit Mic Recorder)
  audio_data = mic_recorder(
      start_prompt="🔴 Mic On (Bolna shuru karein)",
      stop_prompt="⏹️ Rok dein",
      just_once=True,
      key="voice_input",
  )


# Purani messages screen par dikhana
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])


# Function to handle AI response and save to DB
def process_and_respond(user_text):
  # User message session aur DB mein save karna
  st.session_state.messages.append({"role": "user", "content": user_text})
  cursor.execute(
      "INSERT INTO messages (role, content) VALUES (?, ?)", ("user", user_text)
  )
  conn.commit()

  with st.chat_message("user"):
    st.markdown(user_text)

  # AI ka jawab lana
  with st.chat_message("assistant"):
    try:
      response = client.chat.completions.create(
          model="openai/gpt-oss-20b",
          messages=[
              {"role": m["role"], "content": m["content"]}
              for m in st.session_state.messages
          ],
      )
      reply = response.choices[0].message.content
      st.markdown(reply)

      # Assistant ka jawab session aur DB mein save karna
      st.session_state.messages.append({"role": "assistant", "content": reply})
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("assistant", reply),
      )
      conn.commit()
    except Exception as e:
      st.error(f"Error: {e}")


# --- 1. Agar Mic se audio record hua hai (Abhi audio bytes milti hain, text conversion ke liye future update kar sakte hain) ---
# Note: Mic recorder audio data deta hai. Filhal text input main primary chat ke liye chal raha hai.
# Agar user ne text type kiya hai toh usko handle karte hain:

# --- CHAT INPUT (Keyboard) ---
if prompt := st.chat_input("Apna sawal yahan poochein..."):
  process_and_respond(prompt)
