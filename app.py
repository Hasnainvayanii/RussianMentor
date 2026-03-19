import streamlit as st
import requests

# --- 1. CONFIG & TOKENS ---
# Ensure 'HUGGINGFACE_TOKEN' is set in your Streamlit Cloud Secrets
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 

# This is the 2026 standard for Qwen 3.5 on Hugging Face
MODEL_ID = "Qwen/Qwen3.5-4B-Instruct" 
API_URL = "https://api-inference.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

st.set_page_config(page_title="Qwen3.5 Urdu-Russian Mentor", layout="centered")

# --- 2. THE SYSTEM PROMPT ---
system_instruction = """
You are a 'Thinking' AI Mentor. You teach Russian to Urdu speakers using English for clarity.
For every request:
1. First, provide a very brief 'Grammar Logic' explanation.
2. Provide the translation clearly:
   - [Russian Cyrillic]
   - [Urdu Phonetics]
   - [English Meaning]
3. Explain the grammar in simple Urdu (e.g., comparing Russian cases to Urdu 'ka/ki/ko').
"""

# --- 3. UI LAYOUT ---
st.title("🇷🇺 Qwen3.5 Pro Mentor")
st.subheader("Learn Russian through Urdu & English")

# Sidebar for controls
with st.sidebar:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    st.info("Using Qwen3.5-4B via Hugging Face Cloud")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask: How to say 'I am eating' in Russian?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 4. CLOUD CALL (API REQUEST) ---
    with st.spinner("AI is thinking..."):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
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
            
            elif response.status_code == 503:
                st.warning("The model is waking up on the server. Please wait 15-30 seconds and try again.")
            
            elif response.status_code == 401:
                st.error("Invalid Token! Check your Streamlit Secrets.")
            
            else:
                st.error(f"Server Error {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
