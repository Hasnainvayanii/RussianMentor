import streamlit as st
import requests

# --- 1. CONFIG & TOKENS ---
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 

# In 2026, the Router often requires the 'hf-internal' or direct path
# We will use the most compatible version:
MODEL_ID = "Qwen/Qwen3.5-4B-Instruct" 
API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="Qwen3.5 Urdu-Russian Mentor", layout="centered")

# --- 2. THE SYSTEM PROMPT ---
system_instruction = """
You are a 'Thinking' AI Mentor. You teach Russian to Urdu speakers using English for clarity.
Provide the translation:
- [Russian Cyrillic]
- [Urdu Phonetics]
- [English Meaning]
Explain the grammar in Urdu (e.g., how 'Eating' changes for 'I' vs 'He').
"""

# --- 3. UI ---
st.title("🇷🇺 Qwen3.5 Pro Mentor")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask: I am eating in Russian"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 4. THE ROUTER CALL ---
    with st.spinner("Connecting to Hugging Face Router..."):
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
            # We use a POST request to the V1 Chat endpoint
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['choices'][0]['message']['content']
                with st.chat_message("assistant"):
                    st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            else:
                # This will show us EXACTLY what the server is complaining about
                st.error(f"Router Error {response.status_code}: {response.text}")
                st.info("Try checking if your Hugging Face Token has 'Read' permissions.")

        except Exception as e:
            st.error(f"Connection failed: {e}")
