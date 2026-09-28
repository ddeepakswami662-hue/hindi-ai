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

st.set_page_config(
    page_title="Deepu AI Bot", page_icon="🤖", layout="wide"
)

# Force browser tab title via HTML injection
st.markdown("""
    <script>
        document.title = "Deepu AI Bot";
    </script>
""", unsafe_allow_html=True)

# --- SECURITY & CYBERPUNK CSS ---
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

# --- SECURE API & PASSWORD CHECK ---
if "GROQ_API_KEY" in st.secrets and "APP_PASSWORD" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    CORRECT_PASSWORD = st.secrets["APP_PASSWORD"]
else:
    st.error(
        "Missing API Key or App Password in Streamlit Secrets! Please configure"
        " them."
    )
    st.stop()


# --- PASSWORD LOCK SCREEN GATE ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
            <div style='text-align: center; margin-top: 100px;'>
                <h1 style='color: #00ffcc;'>🔒 SECURITY LOCKDOWN PROTOCOL</h1>
                <p style='color: #9ca3af;'>This system belongs exclusively to Deepu. Unauthorized access is blocked.</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            entered_pwd = st.text_input(
                "Enter Access Passcode:",
                type="password",
                placeholder="Passcode daalein...",
            )
            if st.button("Unlock System"):
                if entered_pwd == CORRECT_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error(
                        "⚠️ Access Denied! Galat Passcode. Sirf Master user ko permission"
                        " hai."
                    )
        st.stop()


# Run security check
check_password()

# --- TOP HEADER BANNER ---
st.markdown("""
    <div class="top-header-banner">
        <div>
            <h1 class="top-header-title">🤖 Deepu AI Bot</h1>
            <p class="top-header-subtitle">JARVIS & FRIDAY Autonomous OS • Iron Man Mode Active</p>
        </div>
        <div style="text-align: right;">
            <span style="background: #065f46; color: #34d399; padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">● SECURED & ONLINE</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# --- DATABASE SETUP ---
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memory (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    return conn, cursor


conn, cursor = init_db()

cursor.execute("SELECT role, content FROM messages")
db_messages = cursor.fetchall()

if "messages" not in st.session_state:
    st.session_state.messages = []
    for role, content in db_messages:
        st.session_state.messages.append({"role": role, "content": content})


# --- LIVE WEATHER FETCH ---
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


# --- SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.markdown("### 🛡️ IRON MAN PROTOCOL: ACTIVE")

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
    st.subheader("🔊 Audio / Voice Settings")
    enable_tts = st.checkbox(
        "JARVIS Voice Output (Auto-Speak)",
        value=True,
        help="AI apne jawaab ko khud bol kar sunayega.",
    )

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
    st.subheader("🎙️ Iron Man Mic Control")
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
            f"You are Deepu AI, operating under JARVIS and FRIDAY protocols. You"
            f" serve only Deepu (Boss) with supreme loyalty. Keep answers sharp,"
            f" technical, and helpful. {base_context}"
        )
    elif persona_mode == "Desi Dost & Shayari Mode":
        return (
            f"You are Deepu AI, a warm Indian best friend who speaks Hinglish. {base_context}"
        )
    else:
        return (
            f"You are Deepu AI, a strict, technical professor. {base_context}"
        )


# --- TEXT-TO-SPEECH (IRON MAN VOICE ENGINE) ---
def speak_text(text):
    if enable_tts:
        clean_text = (
            text.replace('"', "")
            .replace("'", "")
            .replace("\n", " ")
            .replace("`", "")
        )
        js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{clean_text}");
                msg.lang = 'hi-IN';
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        components.html(js_code, height=0)


# --- LIVE WEB SEARCH MODULE ---
if search_btn and search_query:
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(search_query, max_results=3, region='wt-wt', safesearch='off')]
        search_summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results]) if results else "No direct results found."
        prompt = f"Live Search Results for '{search_query}':\n{search_summary}\n\nIn results ke adhaar par clear jawab Hindi mein dein:"

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

        summary_prompt = f"Is website content ka summary Hindi mein likho:\n\n{text_content}"

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


# --- PDF ANALYZER MODULE ---
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

        doc_prompt = f"Yeh uploaded document/file hai. Iska analysis Hindi mein batao:\n\n{file_text}"

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


# --- CORE RESPONSE PROCESSOR WITH OPENAI GPT-OSS-20B MODEL ---
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
            # Automatically fetch live web results securely
            search_context = ""
            try:
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(user_text, max_results=3, region='wt-wt', safesearch='off')]
                    if results:
                        search_context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            except Exception:
                pass

            chat_history_payload = [
                {"role": "system", "content": get_system_prompt()}
            ]

            # Inject real-time search context
            if search_context:
                chat_history_payload.append({
                    "role": "system",
                    "content": f"Live Web Search Results for query '{user_text}':\n{search_context}\nUse these real-time internet facts to answer accurately."
                })

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


# --- VOICE TRANSCRIPTION & HANDLING ---
if audio_data and "bytes" in audio_data:
    try:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data["bytes"])
        with open("temp_audio.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3", file=("temp_audio.wav", audio_file.read())
            )
            voice_text = transcript.text
            if voice_text:
                process_and_respond(voice_text)
    except Exception as e:
        st.error(f"Voice processing error: {e}")


# --- RENDER CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- CHAT INPUT (TEXT) ---
if prompt := st.chat_input("JARVIS / Deepu AI se command dein..."):
    process_and_respond(prompt)
