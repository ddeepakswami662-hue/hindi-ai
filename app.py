from datetime import datetime, timedelta, timezone
import sqlite3
import requests
from bs4 import BeautifulSoup
from groq import Groq
import streamlit as st
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Deepu AI - JARVIS Edition", page_icon="⚡", layout="wide"
)

# --- CSS FIX FOR TEXT VISIBILITY & CYBERPUNK THEME ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    /* Text input aur select box mein text saaf dikhne ke liye */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        color: #ffffff !important;
        background-color: #1f2937 !important;
    }
    /* Saare general text aur labels ke liye readable white/light color */
    p, label, .stMarkdown, span {
        color: #e5e7eb !important;
    }
    h1, h2, h3 {
        color: #00ffcc !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Deepu AI Bot [JARVIS & FRIDAY PROTOCOL]")

# Streamlit secrets se API key uthana
if "GROQ_API_KEY" in st.secrets:
  client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
  st.error("Groq API Key missing! Please configure it in Streamlit Secrets.")
  st.stop()


# --- DATABASE SETUP (Permanent Memory & History) ---
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


# --- LIVE WEATHER FETCH (Bikaner, India) ---
def get_live_weather():
  weather_info = "Bikaner, India: Clear / Pleasant"
  try:
    res = requests.get("https://wttr.in/Bikaner?format=%t+%C", timeout=3)
    if res.status_code == 200:
      weather_info = res.text.strip()
  except:
    pass
  return weather_info


live_weather = get_live_weather()


# --- SIDEBAR: HOLOGRAPHIC JARVIS DASHBOARD ---
with st.sidebar:
  st.markdown("### 🛡️ SYSTEM STATUS: ONLINE")

  # Live Working Clock with Seconds (JavaScript + IST Timezone)
  st.markdown("🕒 **Live IST Time & Seconds:**")
  clock_html = """
    <div style="font-family: monospace; font-size: 18px; color: #00ffcc; background: #161b22; padding: 12px; border-radius: 6px; text-align: center; border: 1px solid #30363d; font-weight: bold;">
        <span id="clock">Loading...</span>
    </div>
    <script>
    function updateClock() {
        const now = new Date();
        // Convert current time to India Standard Time (IST - UTC + 5:30)
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const istTime = new Date(utc + (3600000 * 5.5));
        
        let hours = istTime.getHours();
        let minutes = istTime.getMinutes();
        let seconds = istTime.getSeconds();
        
        hours = hours < 10 ? '0' + hours : hours;
        minutes = minutes < 10 ? '0' + minutes : minutes;
        seconds = seconds < 10 ? '0' + seconds : seconds;
        
        document.getElementById('clock').innerHTML = hours + ':' + minutes + ':' + seconds;
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """
  components.html(clock_html, height=70)

  st.markdown(f"🌤️ **Weather:** `{live_weather}`")
  st.markdown("---")

  st.subheader("⚙️ AI Persona / Mood")
  persona_mode = st.selectbox(
      "AI Protocol Chuniye:",
      [
          "JARVIS / FRIDAY (Elite Tech Assistant)",
          "Desi Dost & Shayari Mode",
          "Strict Professor / Expert",
      ],
  )

  st.markdown("---")
  st.subheader("🔊 Audio Output (Text-to-Speech)")
  enable_tts = st.checkbox(
      "AI ki Aawaz On Karein (Voice Reply)", value=False
  )

  st.markdown("---")
  st.subheader("🌐 Web URL Summarizer")
  website_url = st.text_input(
      "Website Link yahan daalein:", placeholder="https://example.com"
  )
  summarize_btn = st.button("Website Summarize Karein")

  st.markdown("---")
  st.subheader("📸 Media Upload")
  uploaded_file = st.file_uploader(
      "Photo upload karein:", type=["jpg", "jpeg", "png"]
  )
  if uploaded_file is not None:
    st.success("Photo successfully linked!")

  st.markdown("---")
  st.subheader("🎙️ Voice Input (Mic)")
  audio_data = mic_recorder(
      start_prompt="🔴 Bolna Shuru Karein",
      stop_prompt="⏹️ Rok Dein",
      just_once=True,
      key="voice_input",
  )


# --- SYSTEM PROMPT BUILDER ---
def get_system_prompt():
  ist_time = (
      datetime.now(timezone(timedelta(hours=5, minutes=30)))
      .strftime("%Y-%m-%d %H:%M:%S")
  )
  base_context = (
      f"Current IST Time: {ist_time}, Live Weather: {live_weather}."
  )
  if persona_mode == "JARVIS / FRIDAY (Elite Tech Assistant)":
    return (
        f"You are Deepu AI, operating under JARVIS and FRIDAY protocols (Iron"
        f" Man's advanced AI suit systems). You are highly sophisticated,"
        f" extremely loyal, intelligent, and address the user with supreme"
        f" respect (like Boss/Sir). {base_context}"
    )
  elif persona_mode == "Desi Dost & Shayari Mode":
    return (
        f"You are Deepu AI, a warm Indian best friend who speaks Hinglish,"
        f" drops shayari, and jokes around. {base_context}"
    )
  else:
    return (
        f"You are Deepu AI, a strict, technical professor providing precise"
        f" answers. {base_context}"
    )


# --- TEXT-TO-SPEECH JAVASCRIPT INJECTOR (JARVIS Voice) ---
def speak_text(text):
  if enable_tts:
    clean_text = text.replace('"', "").replace("'", "").replace("\n", " ")
    js_code = f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{clean_text}");
            msg.lang = 'hi-IN';
            window.speechSynthesis.speak(msg);
        </script>
        """
    st.markdown(js_code, unsafe_allow_html=True)


# --- HANDLE WEB URL SUMMARIZER ---
if summarize_btn and website_url:
  try:
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(website_url, headers=headers, timeout=10)
    soup = BeautifulSoup(page.content, "html.parser")
    text_content = " ".join([p.text for p in soup.find_all("p")])
    if len(text_content) > 4000:
      text_content = text_content[:4000]

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
      speak_text(reply)

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
    st.error(f"Website fetch error: {e}")


# --- HANDLE VOICE TRANSCRIPTION (Whisper API) ---
voice_text = None
if audio_data and "bytes" in audio_data:
  try:
    with open("temp_audio.wav", "wb") as f:
      f.write(audio_data["bytes"])
    with open("temp_audio.wav", "rb") as audio_file:
      transcript = client.audio.transcriptions.create(
          model="whisper-large-v3", file=("temp_audio.wav", audio_file.read())
      )
      voice_text = transcript.text
  except Exception as e:
    st.error(f"Voice processing error: {e}")


# --- RENDER CHAT HISTORY ---
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])


# --- CORE RESPONSE PROCESSOR ---
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
      speak_text(reply)

      st.session_state.messages.append({"role": "assistant", "content": reply})
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("assistant", reply),
      )
      conn.commit()
    except Exception as e:
      st.error(f"Error: {e}")


# Process voice text if received
if voice_text:
  process_and_respond(voice_text)

# --- CHAT INPUT (KEYBOARD) ---
if prompt := st.chat_input("JARVIS / Deepu AI se command dein..."):
  process_and_respond(prompt)
