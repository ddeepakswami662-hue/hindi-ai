import streamlit as st
from groq import Groq

st.title("🤖 Hindi AI Chat Bot")

# Streamlit secrets se API key automatically uthayega
if "GROQ_API_KEY" in st.secrets:
   client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Groq API Key missing! Please configure it in Streamlit Secrets.")
    st.stop()

# Chat input aur model call
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Apna sawal yahan poochein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error: {e}")
