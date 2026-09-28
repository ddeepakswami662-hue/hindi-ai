import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="Hindi AI Chat Bot",
    page_icon="🤖",
    layout="centered"
)

# App header
st.title("🤖 Desi Hindi AI Assistant")
st.write("Apni Groq API Key dalein aur khul kar Hindi mein baat karein!")

# Sidebar for API Key
with st.sidebar:
    st.header("🔑 Settings")
    api_key_input = st.text_input("Groq API Key:", type="password", help="Apni Groq API Key yahan paste karein")
    st.markdown("---")
    st.markdown("**Powered by:** Groq (Llama 3) & Streamlit")

# Main Chat Logic
if not api_key_input:
    st.warning("⚠️ Kripya shuru karne ke liye sidebar mein apni Groq API Key dalein.")
else:
    client = Groq(api_key=api_key_input)
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Namaste! Main aapka Hindi AI assistant hoon. Aaj main aapki kya madad kar sakta hoon?"}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input prompt
    if prompt := st.chat_input("Yahan apna sawal Hindi mein likhein..."):
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response from Groq
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Soch raha hoon...")
            
            try:
                # System prompt to ensure Hindi replies
                system_instruction = {
                    "role": "system", 
                    "content": "You are a helpful, smart, and polite AI assistant. Always reply naturally and fluently in Hindi (Devanagari script), unless the user asks in English."
                }
                
                # Format messages for Groq API
                chat_history = [system_instruction] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=chat_history,
                    temperature=0.7,
                    max_tokens=1024,
                )
                
                response_text = completion.choices[0].message.content
                message_placeholder.markdown(response_text)
                
                # Save assistant response
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                message_placeholder.error(f"Koyi error aa gaya hai: {e}")
