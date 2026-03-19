import streamlit as st
import requests

# --- 1. CONFIG & TOKENS ---
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 

# This is the exact URL the Error 410 is asking for:
API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"
# We will try the 7B model because it's more likely to be "awake" on the Router
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct" 

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="Qwen3.5 Urdu-Russian Mentor", layout="centered")

# --- 2. THE SYSTEM PROMPT ---
system_instruction = "You are a Russian teacher. Explain in Urdu and English. Provide Cyrillic and Phonetics."

# --- 3. UI ---
st.title("🇷🇺 Russian Mentor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 4. THE ROUTER CALL ---
    with st.spinner("Connecting..."):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "stream": False
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['choices'][0]['message']['content']
                with st.chat_message("assistant"):
                    st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            else:
                st.error(f"Router Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed: {e}")
