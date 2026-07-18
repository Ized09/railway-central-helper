import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper - Debug Mode")
st.caption("v1.4 - Review Debug")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

model_options = {
    "Fable 5 (Creative)": "claude-fable-5",
    "Sonnet 5 (Balanced)": "claude-sonnet-5"
}
selected_model_name = st.sidebar.selectbox("Model", list(model_options.keys()))
selected_model = model_options[selected_model_name]

st.sidebar.success(f"Using: {selected_model_name}")

if st.button("Test API Call"):
    with st.spinner("Testing..."):
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": selected_model,
                    "max_tokens": 100,
                    "messages": [{"role": "user", "content": "Say hello"}]
                },
                timeout=30
            )
            st.write("Status:", resp.status_code)
            data = resp.json()
            st.json(data)
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.info("Use the Test button first, then try generating a review.")
