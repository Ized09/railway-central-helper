import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v1.2 - Fable 5 Fixed")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Fable 5 Connected")

tab1, tab2 = st.tabs(["📋 Thread Helper", "✍️ Humanizer"])

# ====================== HUMANIZER (Fixed) ======================
with tab2:
    st.subheader("✍️ Humanizer (Fable 5)")
    ai_text = st.text_area("Paste AI-generated text here:", height=250)
    
    if st.button("✨ Humanize with Fable 5", type="primary"):
        if ai_text.strip():
            with st.spinner("Humanizing..."):
                prompt = f"""Rewrite this to sound like a real helpful human on Railway Central Station. Natural and friendly.

Original:
{ai_text}"""

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
                            "max_tokens": 1200,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    data = resp.json()
                    
                    # Extract text from content blocks
                    text_parts = []
                    for block in data.get("content", []):
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    
                    humanized = "\n".join(text_parts)
                    st.session_state.humanized = humanized
                    
                    st.success("Done!")
                    st.markdown(humanized)
                    
                    if st.button("📋 Copy"):
                        st.code(humanized, language=None)
                        st.success("Copied!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.write("Raw response:", data if 'data' in locals() else "No data")
        else:
            st.warning("Paste text first.")

# (You can keep the Thread Helper tab from previous versions)

st.sidebar.info("Fable 5 is working now")
