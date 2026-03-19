import streamlit as st
import requests

# --- 1. CONFIG & TOKENS ---
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 
MODEL_ID = "Qwen/Qwen3.5-4B-Instruct" # Using the Instruct version for better chat
# NEW 2026 ROUTER URL
API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="Qwen3.5 Urdu-Russian Mentor", layout="centered")

# --- 2. THE SYSTEM PROMPT ---
system_instruction = """
You are a 'Thinking' AI Mentor. You teach Russian to Urdu speakers using English for clarity.
For every request:
1. First, reason about the grammar logic.
2. Provide:
   - [Russian Cyrillic]
   - [Urdu Phonetics]
   - [English Meaning]
   - A short explanation in Urdu comparing it to Urdu grammar.
"""

# --- 3. UI ---
st.title("🇷🇺 Qwen3.5 Pro Mentor")
st.info("Mode: 3-Language (Urdu + English -> Russian)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask: How to say 'How are you?'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 4. CLOUD CALL (Updated for Router) ---
    with st.spinner("Qwen3.5 is thinking..."):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 800,
            "temperature": 0.7
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            # The answer is now nested in 'choices'
            ai_text = result['choices'][0]['message']['content']
            with st.chat_message("assistant"):
                st.markdown(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
        elif response.status_code == 503:
            st.warning("The AI is warming up. Please wait 20 seconds and try again!")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
