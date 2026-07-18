import streamlit as st
import requests
import os
import re

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.3 - Real-time Helper with AI Review + Copy")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not found in Railway Variables.")
    st.stop()

QUERY = """
{
  threads(first: 20, sort: recent_activity) {
    edges {
      node {
        slug
        subject
        status
        topic { displayName }
        upvoteCount
        createdAt
        content { data }
      }
    }
  }
}
"""

def fetch_threads():
    try:
        resp = requests.post("https://station-server.railway.com/gql", json={"query": QUERY})
        return resp.json()["data"]["threads"]["edges"]
    except:
        st.error("Could not fetch threads")
        return []

def get_ai_review(thread_subject, content):
    prompt = f"""You are a helpful senior Railway engineer on Central Station.

Thread: {thread_subject}
Content: {content[:8000]}

Write a friendly, professional reply that includes:
- Quick summary
- Likely cause
- Suggested fix
- Ready-to-post reply (keep it kind and actionable)
"""

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
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

# Main UI
col1, col2 = st.columns([3,1])
with col1:
    if st.button("🔄 Refresh Recent Threads", type="primary"):
        with st.spinner("Loading from Central Station..."):
            threads = fetch_threads()
            
            for edge in threads:
                node = edge["node"]
                content = node.get("content", {}).get("data", "")
                is_bounty = "$" in node["subject"] or "bounty" in node["subject"].lower()
                
                with st.expander(f"{'💰 ' if is_bounty else ''}{node['subject']} • {node['topic']['displayName']} • {node['upvoteCount']} votes"):
                    st.caption(f"Status: {node['status']} | {node['createdAt'][:10]}")
                    st.write(content[:600] + "..." if len(content) > 600 else content)
                    
                    if st.button("🤖 Get AI Review", key=node["slug"]):
                        with st.spinner("Claude thinking..."):
                            review = get_ai_review(node["subject"], content)
                            st.markdown("### AI Review & Suggested Reply")
                            st.markdown(review)
                            
                            # Copy button
                            if st.button("📋 Copy Reply", key=f"copy_{node['slug']}"):
                                st.code(review, language="markdown")
                                st.success("Copied to clipboard! (manual copy for now)")

st.sidebar.success("✅ Server-side Anthropic key loaded")
st.sidebar.info("💡 Tip: Look for 💰 threads with bounties!")
