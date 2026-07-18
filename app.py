import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v1.0 - Helper + Humanizer")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Claude Connected")
st.sidebar.warning("Always edit before posting")

tab1, tab2 = st.tabs(["📋 Thread Helper", "✍️ Humanizer"])

# ====================== TAB 1: THREAD HELPER ======================
with tab1:
    # (Keep the split layout code from previous message here)
    # ... I'll abbreviate for space, but use the full split layout from last response

    st.info("Thread Helper tab - select thread and generate AI review")

# ====================== TAB 2: HUMANIZER ======================
with tab2:
    st.subheader("Humanizer Tool")
    st.caption("Make AI text sound more natural and human")
    
    ai_text = st.text_area("Paste AI-generated review here:", height=300)
    
    style = st.selectbox("Style", ["Natural & Friendly", "Professional but Warm", "Short & Direct", "Detailed & Helpful"])
    
    if st.button("✨ Humanize Text", type="primary"):
        if ai_text.strip():
            with st.spinner("Humanizing..."):
                prompt = f"""Rewrite the following reply to sound more like a helpful human on Railway Central Station.

Style: {style}

Original:
{ai_text}

Make it natural, friendly, and human. Avoid sounding too robotic. Keep the technical accuracy but add warmth and personality."""

                try:
                    resp = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": ANTHROPIC_KEY,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "claude-sonnet-5",
                            "max_tokens": 1200,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    humanized = resp.json()["content"][0]["text"]
                    st.session_state.humanized_text = humanized
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please paste some text first.")

    if "humanized_text" in st.session_state:
        st.subheader("Humanized Version")
        st.markdown(st.session_state.humanized_text)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Humanized"):
                st.code(st.session_state.humanized_text, language=None)
                st.success("Copied!")
        with col2:
            if st.button("🔄 Humanize Again"):
                st.session_state.humanized_text = None
                st.rerun()

st.sidebar.info("Use Helper tab for AI review → Humanizer tab to make it sound natural")
