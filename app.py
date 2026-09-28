import streamlit as st
from groq import Groq

st.title("🤖 Hindi AI Chat Bot")

# Streamlit secrets se API key uthana
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Groq API Key missing! Please configure it in Streamlit Secrets.")
    st.stop()

# 1. Chat History (Session State) - Yeh purani baatein yaad rakhega
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani messages screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Camera / Image Upload ka option sidebar mein
with st.sidebar:
    st.header("📸 Media Upload")
    uploaded_file = st.file_uploader("Apni photo ya koi image upload karein:", type=["jpg", "jpeg", "png"])
    
    # Agar aap chahein toh camera se seedha photo lene ka feature bhi hai:
    # use_camera = st.camera_input("Camera se photo lein")

# 3. Chat Input (Yeh mic aur text dono support karta hai)
if prompt := st.chat_input("Apna sawal yahan poochein... (Mic ya Keyboard se)"):
    
    # User message save aur display karna
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI ka jawab lana
    with st.chat_message("assistant"):
        try:
            # Groq API ko messages bhejna (History ke sath)
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
