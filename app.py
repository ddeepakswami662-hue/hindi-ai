import sqlite3
import streamlit as st
from groq import Groq

st.title("🤖 Hindi AI Chat Bot (Permanent History)")

# Streamlit secrets se API key uthana
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Groq API Key missing! Please configure it in Streamlit Secrets.")
    st.stop()


# --- DATABASE SETUP ---
def init_db():
  conn = sqlite3.connect("chat_history.db", check_same_thread=False)
  cursor = conn.cursor()
  # Ek table banate hain jo messages store karegi
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

# Database se purani saari messages load karna
cursor.execute("SELECT role, content FROM messages")
db_messages = cursor.fetchall()

# Session state mein load karna taaki screen par dikhe
if "messages" not in st.session_state:
  st.session_state.messages = []
  for role, content in db_messages:
    st.session_state.messages.append({"role": role, "content": content})

# Purani messages screen par dikhana
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# --- CHAT INPUT & DATABASE SAVE ---
if prompt := st.chat_input("Apna sawal yahan poochein..."):
  # User message session aur DB mein save karna
  st.session_state.messages.append({"role": "user", "content": prompt})
  cursor.execute(
      "INSERT INTO messages (role, content) VALUES (?, ?)", ("user", prompt)
  )
  conn.commit()

  with st.chat_message("user"):
    st.markdown(prompt)

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
