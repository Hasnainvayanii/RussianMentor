import streamlit as st
import requests

# --- 1. CONFIG & TOKENS ---
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 
MODEL_ID = "Qwen/Qwen3.5-4B-Instruct" 

# Using the Model-Specific v1 Endpoint (Most stable for 404 errors)
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}/v1/chat/completions"

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

    # --- 4. THE CALL ---
    with st.spinner("Talking to Qwen3.5..."):
        payload = {
            "model": "tgi", # This tells Hugging Face to use the Text Generation Inference engine
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500
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
                st.error(f"Error {response.status_code}: {response.text}")
                st.info("If you see 404, the model might be temporarily offline. Try again in 2 minutes.")

        except Exception as e:
            st.error(f"Connection failed: {e}")
            
