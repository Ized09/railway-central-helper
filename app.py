import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Helper Debug", layout="wide")
st.title("🚄 Railway Central Station AI Helper - Debug Mode")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not found in Variables.")
    st.stop()

st.success("Key loaded successfully!")

if st.button("Test Claude API Call"):
    with st.spinner("Calling Claude..."):
        try:
            payload = {
                "model": "claude-3-5-sonnet-20240620",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": "Say hello and confirm you are working."}]
            }
            
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            st.write("Status code:", resp.status_code)
            
            if resp.status_code == 200:
                result = resp.json()
                st.success("Success!")
                st.write(result["content"][0]["text"])
            else:
                st.error(f"API Error: {resp.text}")
        except Exception as e:
            st.error(f"Exception: {str(e)}")

st.info("If this Test button works, the full version will work too.")
