import sqlite3
import streamlit as st
from bs4 import BeautifulSoup
import requests
from groq import Groq
from streamlit_mic_recorder import mic_recorder

# --- PAGE CONFIG ---
st.set_page_config(page_title="Deepu AI Bot", page_icon="🤖", layout="wide")

st.title("🤖 Deepu AI Bot - Ultimate Edition")

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


# --- SIDEBAR: ULTIMATE CONTROLS ---
with st.sidebar:
  st.header("⚙️ Advanced Controls")

  # 1. Persona / Mood Selector
  st.subheader("🎭 AI ka Mizaj (Persona)")
  persona_mode = st.selectbox(
      "Deepu AI ka andaz chuniye:",
      [
          "Desi Dost & Shayari Mode",
          "Strict Professor / Tech Expert",
          "Sarcastic & Comedy Mode",
      ],
  )

  st.markdown("---")

  # 2. Web URL Summarizer
  st.subheader("🌐 Web URL Summarizer")
  website_url = st.text_input(
      "Website ka Link (URL) yahan daalein:", placeholder="https://example.com"
  )
  summarize_btn = st.button("Website Summarize Karein")

  st.markdown("---")

  # 3. Photo Upload
  st.subheader("📸 Media Upload")
  uploaded_file = st.file_uploader(
      "Photo upload karein:", type=["jpg", "jpeg", "png"]
  )
  if uploaded_file is not None:
    st.success("Photo upload ho gayi!")

  st.markdown("---")

  # 4. Voice Input (Mic)
  st.subheader("🎙️ Voice Input")
  audio_data = mic_recorder(
      start_prompt="🔴 Bolna Shuru Karein",
      stop_prompt="⏹️ Rok Dein",
      just_once=True,
      key="voice_input",
  )


# --- SYSTEM PROMPT BUILDER BASED ON PERSONA ---
def get_system_prompt():
  if persona_mode == "Desi Dost & Shayari Mode":
    return "You are Deepu AI, a friendly, warm Indian best friend who speaks fluent Hindi/Hinglish, occasionally drops fun poetry (shayari), and talks with full warmth and desi style."
  elif persona_mode == "Strict Professor / Tech Expert":
    return "You are Deepu AI, a strict, highly intellectual professor and elite tech expert. You provide precise, structured, and deep factual answers without any unnecessary fluff."
  else:
    return "You are Deepu AI, a witty, slightly sarcastic, and humorous assistant who loves gentle teasing and comedy while still helping out."


# --- HANDLE WEB URL SUMMARIZER ACTION ---
if summarize_btn and website_url:
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(website_url, headers=headers, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")

    # Saara text nikalna
    text_content = " ".join([p.text for p in soup.find_all("p")])
    if len(text_content) > 4000:
      text_content = text_content[:4000]  # Limit length

    summary_prompt = f"Is website content ka ek shandar aur clear summary Hindi mein likho:\n\n{text_content}"

    with st.chat_message("user"):
      st.markdown(f"🌐 **Website Summary Request:** {website_url}")

    with st.chat_message("assistant"):
      response = client.chat.completions.create(
          model="openai/gpt-oss-20b",
          messages=[
              {"role": "system", "content": get_system_prompt()},
              {"role": "user", "content": summary_prompt},
          ],
      )
      reply = response.choices[0].message.content
      st.markdown(reply)

      # Save to DB
      st.session_state.messages.append(
          {"role": "user", "content": f"Website Summary: {website_url}"}
      )
      st.session_state.messages.append({"role": "assistant", "content": reply})
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("user", f"Website Summary: {website_url}"),
      )
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("assistant", reply),
      )
      conn.commit()
  except Exception as e:
    st.error(f"Website fetch karne mein error aayi: {e}")


# --- HANDLE VOICE INPUT (AUDIO DATA) ---
voice_text = None
if audio_data and "bytes" in audio_data:
  try:
    # Groq Whisper API se audio ko text mein convert karna
    with open("temp_audio.wav", "wb") as f:
      f.write(audio_data["bytes"])

    with open("temp_audio.wav", "rb") as audio_file:
      transcript = client.audio.transcriptions.create(
          model="whisper-large-v3", file=("temp_audio.wav", audio_file.read())
      )
      voice_text = transcript.text
  except Exception as e:
    st.error(f"Voice processing error: {e}")


# --- PURANI MESSAGES SCREEN PAR DIKHANA ---
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])


# --- MAIN CHAT FUNCTION ---
def process_and_respond(user_text):
  st.session_state.messages.append({"role": "user", "content": user_text})
  cursor.execute(
      "INSERT INTO messages (role, content) VALUES (?, ?)", ("user", user_text)
  )
  conn.commit()

  with st.chat_message("user"):
    st.markdown(user_text)

  with st.chat_message("assistant"):
    try:
      # Messages list taiyar karna with dynamic Persona system prompt
      chat_history_payload = [
          {"role": "system", "content": get_system_prompt()}
      ]
      for m in st.session_state.messages:
        chat_history_payload.append(
            {"role": m["role"], "content": m["content"]}
        )

      response = client.chat.completions.create(
          model="openai/gpt-oss-20b", messages=chat_history_payload
      )
      reply = response.choices[0].message.content
      st.markdown(reply)

      st.session_state.messages.append({"role": "assistant", "content": reply})
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("assistant", reply),
      )
      conn.commit()
    except Exception as e:
      st.error(f"Error: {e}")


# Agar mic se text aaya hai toh use auto-process karo
if voice_text:
  process_and_respond(voice_text)

# --- CHAT INPUT (KEYBOARD) ---
if prompt := st.chat_input("Deepu AI se kuch bhi poochein..."):
  process_and_respond(prompt)
