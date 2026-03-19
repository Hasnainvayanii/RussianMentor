import streamlit as st
import requests
import time

# --- 1. CONFIG & TOKENS ---
# Replace with your new token or set in Streamlit Secrets
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"] 
MODEL_ID = "Qwen/Qwen3.5-4B"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="Qwen3.5 Urdu-Russian Mentor", layout="centered")

# --- 2. THE SYSTEM PROMPT ---
system_instruction = """
You are a 'Thinking' AI Mentor. You teach Russian to Urdu speakers using English for clarity.
For every request:
1. Inside <think> tags, analyze the grammar and translation logic.
2. In the final response, provide:
   - [Russian Cyrillic]
   - [Urdu Phonetics]
   - [English Meaning]
   - A short explanation in Urdu.
"""

# --- 3. UI ---
st.title("🇷🇺 Qwen3.5 Pro Mentor")
st.info("Mode: 3-Language (Urdu + English -> Russian)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask me anything... (e.g. How to say 'I am a student'?)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 4. CLOUD CALL ---
    with st.spinner("Qwen3.5 is thinking..."):
        # We format the prompt to trigger the 'Thinking' architecture
        formatted_prompt = f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>\n"
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            full_response = response.json()[0]['generated_text']
            # Cleaning the output to show the 'Think' and 'Result' clearly
            with st.chat_message("assistant"):
                st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            st.error(f"Error: {response.status_code}. The model might be loading on Hugging Face. Wait 30 seconds.")
