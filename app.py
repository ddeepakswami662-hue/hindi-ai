from datetime import datetime, timedelta, timezone
import io
import sqlite3
import traceback
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from groq import Groq
import pypdf
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Deepu AI - JARVIS OS", page_icon="⚡", layout="wide"
)

# --- ADVANCED CYBERPUNK CSS & PERMANENT TOP HEADER ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .top-header-banner {
        background: linear-gradient(90deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .top-header-title {
        color: #00ffcc !important;
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        letter-spacing: 1px;
    }
    .top-header-subtitle {
        color: #9ca3af !important;
        font-size: 14px;
        margin: 0;
    }
    .stTextInput input, .stTextArea textarea {
        color: #ffffff !important;
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        color: #ffffff !important;
        background-color: #1f2937 !important;
    }
    label, .stMarkdown, span, p {
        color: #f3f4f6 !important;
    }
    h2, h3 {
        color: #00ffcc !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Top Header Banner
st.markdown("""
    <div class="top-header-banner">
        <div>
            <h1 class="top-header-title">🤖 Deepu AI Bot</h1>
            <p class="top-header-subtitle">JARVIS & FRIDAY Autonomous OS • Ultimate Edition</p>
        </div>
        <div style="text-align: right;">
            <span style="background: #065f46; color: #34d399; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">● SYSTEM ONLINE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Streamlit secrets se API key uthana
if "GROQ_API_KEY" in st.secrets:
  client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
  st.error("Groq API Key missing! Please configure it in Streamlit Secrets.")
  st.stop()


# --- DATABASE SETUP (Permanent Memory & User Profiles) ---
def init_db():
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  cursor = conn.cursor()
  # Chat Messages Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
  # User Memory Table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
  conn.commit()
  return conn, cursor


conn, cursor = init_db()

# Load chat history
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


# --- SIDEBAR: ULTIMATE JARVIS CONTROL CENTER ---
with st.sidebar:
  st.markdown("### 🛡️ SYSTEM STATUS")

  # Live IST Clock with Seconds
  clock_html = """
    <div style="font-family: monospace; font-size: 15px; color: #00ffcc; background: #1f2937; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #374151; font-weight: bold; margin-bottom: 10px;">
        🕒 IST: <span id="clock">Loading...</span>
    </div>
    <script>
    function updateClock() {
        const now = new Date();
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
  components.html(clock_html, height=45)

  st.markdown(f"🌤️ **Weather:** `{live_weather}`")
  st.markdown("---")

  st.subheader("⚙️ AI Protocol / Mood")
  persona_mode = st.selectbox(
      "AI Protocol Chuniye:",
      [
          "JARVIS / FRIDAY (Elite Tech Assistant)",
          "Desi Dost & Shayari Mode",
          "Strict Professor / Expert",
      ],
      label_visibility="collapsed",
  )

  st.markdown("---")
  st.subheader("🔊 Audio Output")
  enable_tts = st.checkbox("AI ki Aawaz (Voice Reply)", value=False)

  st.markdown("---")
  st.subheader("🌐 Live Web Search")
  search_query = st.text_input(
      "Google/DDG Search:", placeholder="Khabar ya info search karein..."
  )
  search_btn = st.button("Search Karein")

  st.markdown("---")
  st.subheader("🔗 Web URL Summarizer")
  website_url = st.text_input(
      "Website Link:", placeholder="https://example.com"
  )
  summarize_btn = st.button("Summarize Karein")

  st.markdown("---")
  st.subheader("📄 PDF & Document Reader")
  uploaded_pdf = st.file_uploader(
      "PDF ya Code File upload karein:", type=["pdf", "txt", "py"]
  )
  pdf_analyze_btn = st.button("File Analysing Karein")

  st.markdown("---")
  st.subheader("🎙️ Voice Input")
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
  # Fetch stored user memory
  cursor.execute("SELECT key, value FROM user_memory")
  memories = cursor.fetchall()
  memory_context = (
      ", ".join([f"{k}: {v}" for k, v in memories])
      if memories
      else "No saved memory yet."
  )

  base_context = f"Current IST Time: {ist_time}, Live Weather: {live_weather}. Permanent User Memory: {memory_context}"

  if persona_mode == "JARVIS / FRIDAY (Elite Tech Assistant)":
    return (
        f"You are Deepu AI, operating under JARVIS and FRIDAY protocols (Iron"
        f" Man's advanced AI suit systems). You are highly sophisticated,"
        f" loyal, and address the user with supreme respect (Boss/Sir)."
        f" {base_context}"
    )
  elif persona_mode == "Desi Dost & Shayari Mode":
    return (
        f"You are Deepu AI, a warm Indian best friend who speaks Hinglish and"
        f" drops shayari. {base_context}"
    )
  else:
    return (
        f"You are Deepu AI, a strict, technical professor providing precise"
        f" answers. {base_context}"
    )


# --- TEXT-TO-SPEECH JAVASCRIPT INJECTOR ---
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


# --- LIVE WEB SEARCH MODULE ---
if search_btn and search_query:
  try:
    with DDGS() as ddgs:
      results = [r for r in ddgs.text(search_query, max_results=3)]
    search_summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])

    prompt = f"Live Search Results for '{search_query}':\n{search_summary}\n\nIn results ke adhaar par ek behtareen aur clear jawab Hindi mein dein:"

    with st.chat_message("user"):
      st.markdown(f"🔍 **Live Search:** {search_query}")

    with st.chat_message("assistant"):
      response = client.chat.completions.create(
          model="openai/gpt-oss-20b",
          messages=[
              {"role": "system", "content": get_system_prompt()},
              {"role": "user", "content": prompt},
          ],
      )
      reply = response.choices[0].message.content
      st.markdown(reply)
      speak_text(reply)

      st.session_state.messages.append(
          {"role": "user", "content": f"Search: {search_query}"}
      )
      st.session_state.messages.append({"role": "assistant", "content": reply})
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("user", f"Search: {search_query}"),
      )
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("assistant", reply),
      )
      conn.commit()
  except Exception as e:
    st.error(f"Search error: {e}")


# --- WEB URL SUMMARIZER MODULE ---
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


# --- PDF / DOCUMENT ANALYZER MODULE ---
if pdf_analyze_btn and uploaded_pdf is not None:
  try:
    file_text = ""
    if uploaded_pdf.name.endswith(".pdf"):
      reader = pypdf.PdfReader(uploaded_pdf)
      for page in reader.pages:
        file_text += page.extract_text() or ""
    else:
      file_text = uploaded_pdf.read().decode("utf-8")

    if len(file_text) > 4000:
      file_text = file_text[:4000]

    doc_prompt = f"Yeh ek uploaded document/file hai. Iska pura analysis aur summary Hindi mein batao:\n\n{file_text}"

    with st.chat_message("user"):
      st.markdown(f"📄 **Document Analyzed:** `{uploaded_pdf.name}`")

    with st.chat_message("assistant"):
      response = client.chat.completions.create(
          model="openai/gpt-oss-20b",
          messages=[
              {"role": "system", "content": get_system_prompt()},
              {"role": "user", "content": doc_prompt},
          ],
      )
      reply = response.choices[0].message.content
      st.markdown(reply)
      speak_text(reply)

      st.session_state.messages.append(
          {"role": "user", "content": f"Analyzed File: {uploaded_pdf.name}"}
      )
      st.session_state.messages.append({"role": "assistant", "content": reply})
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("user", f"Analyzed File: {uploaded_pdf.name}"),
      )
      cursor.execute(
          "INSERT INTO messages (role, content) VALUES (?, ?)",
          ("assistant", reply),
      )
      conn.commit()
  except Exception as e:
    st.error(f"Document processing error: {e}")


# --- VOICE TRANSCRIPTION (Whisper API) ---
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


# --- CORE RESPONSE PROCESSOR & CODE EXECUTION SANDBOX ---
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

      # --- SPECIAL SANDBOX: Agar user ne python code run karne ko kaha ho ---
      if "run code" in user_text.lower() or "execute" in user_text.lower():
        if "```python" in reply:
          try:
            code_str = reply.split("```python")[1].split("```")[0]
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            exec(code_str, {})
            sys.stdout = old_stdout
            output_result = new_stdout.getvalue()
            if output_result:
              exec_msg = f"⚙️ **Sandbox Output:**\n```\n{output_result}\n```"
              st.markdown(exec_msg)
              reply += f"\n\n{exec_msg}"
          except Exception as code_err:
            pass

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
