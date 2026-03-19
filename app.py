import streamlit as st
import requests

# --- 1. CONFIG & TOKENS ---
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 

# The specific 2026 Router endpoint
MODEL_ID = "Qwen/Qwen3.5-4B-Instruct" 
API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="Qwen3.5 Urdu-Russian Mentor", layout="centered")

# --- 2. THE SYSTEM PROMPT ---
system_instruction = """
You are a professional Russian Mentor for Urdu speakers. 
1. Explain grammar using Urdu analogies.
2. Provide Russian Cyrillic + Urdu Phonetics + English translation.
3. Example: [Привет] - [پریویت] - [Hello].
"""

# --- 3. UI LAYOUT ---
st.title("🇷🇺 Qwen3.5 Pro Mentor")
st.subheader("Urdu-Russian Language Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask: How to say 'I am eating' in Russian?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 4. THE ROUTER CALL ---
    with st.spinner("Connecting to Qwen3.5..."):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['choices'][0]['message']['content']
                with st.chat_message("assistant"):
                    st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            elif response.status_code == 410:
                st.error("The API endpoint has changed again. Please check Hugging Face documentation.")
            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Connection failed: {e}")
