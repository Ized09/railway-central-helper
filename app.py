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
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-5-sonnet-20240620",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": "Say hello and confirm you are working."}]
                }
            )
            result = resp.json()
            st.success("Success!")
            st.write(result["content"][0]["text"])
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Status code:", resp.status_code if 'resp' in locals() else "No response")

st.info("If the Test button works, the full review feature will work too.")
