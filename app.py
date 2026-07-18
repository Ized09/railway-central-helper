import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.4 - Bounty Focus + Copy Button")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
RAILWAY_TOKEN = os.getenv("RAILWAY_TOKEN")  # Optional for future features

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set in Railway Variables.")
    st.stop()

# ... (same QUERY and functions as before)

def fetch_threads():
    # same as previous

def get_ai_review(...):
    # same as previous

# UI with filters
show_bounties_only = st.checkbox("Show only Bounty threads 💰", value=True)

if st.button("🔄 Refresh Threads"):
    with st.spinner("Loading..."):
        threads = fetch_threads()
        
        for edge in threads:
            node = edge["node"]
            subject = node["subject"].lower()
            is_bounty = "$" in subject or "bounty" in subject
            
            if show_bounties_only and not is_bounty:
                continue
                
            with st.expander(f"{'💰 ' if is_bounty else ''}{node['subject']}"):
                st.caption(f"Topic: {node['topic']['displayName']} | Votes: {node['upvoteCount']}")
                content = node.get("content", {}).get("data", "")
                st.write(content[:700] + "..." if len(content) > 700 else content)
                
                if st.button("🤖 Get AI Review", key=node["slug"]):
                    with st.spinner("Claude is working..."):
                        review = get_ai_review(node["subject"], content)
                        st.markdown(review)
                        
                        # Copy button
                        if st.button("📋 Copy to Clipboard", key=f"copy_{node['slug']}"):
                            st.code(review, language=None)
                            st.success("Copied! Paste it in Central Station.")

st.sidebar.success("✅ Ready for bounties")
if RAILWAY_TOKEN:
    st.sidebar.success("Railway token loaded")
