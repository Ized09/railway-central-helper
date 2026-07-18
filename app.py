import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper - Debug Mode")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

st.sidebar.success("✅ Key Loaded")
st.sidebar.info("Fable 5 Test")

ai_text = st.text_area("Paste text to test:", height=200)

if st.button("Test Fable 5 Call"):
    with st.spinner("Calling Fable 5..."):
        prompt = f"""Rewrite this to sound natural and human:\n\n{ai_text}"""

        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-fable-5",
                    "max_tokens": 800,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            st.write("**Status Code:**", resp.status_code)
            data = resp.json()
            st.json(data)  # Show full response for debugging
            
            if "content" in data and len(data["content"]) > 0:
                st.success("Success!")
                st.write(data["content"][0]["text"])
            else:
                st.error("No 'content' in response")
        except Exception as e:
            st.error(f"Exception: {str(e)}")
            st.write("Raw response:", resp.text if 'resp' in locals() else "No response")

st.info("Paste some text and click the button to see the full API response.")
