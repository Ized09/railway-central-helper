import streamlit as st
import requests
import os
import traceback

st.set_page_config(page_title="Railway Helper - Debug", layout="wide")
st.title("🚄 Railway Central Station AI Helper - Full Debug")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

st.sidebar.success(f"Key loaded: {'Yes' if ANTHROPIC_KEY else 'No'}")

if st.button("Test Simple Claude Call"):
    with st.spinner("Testing..."):
        try:
            payload = {
                "model": "claude-sonnet-5",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": "Say hello"}]
            }
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            st.write("Status:", resp.status_code)
            st.write("Response:", resp.text[:500])
        except Exception as e:
            st.error(f"Exception: {str(e)}")
            st.code(traceback.format_exc())

st.info("Click the button above to test the API call.")
