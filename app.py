import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.5 - Fixed Review")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Claude Ready")

QUERY = """
{
  threads(first: 15, sort: recent_activity) {
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
    prompt = f"""You are a helpful senior Railway engineer.

Thread Title: {thread_subject}

Content: {content[:6000]}

Write a friendly, useful reply to this user. Be concise and actionable."""

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
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

# UI
if st.button("🔄 Refresh Recent Threads", type="primary"):
    with st.spinner("Loading..."):
        threads = fetch_threads()
        
        for edge in threads:
            node = edge["node"]
            with st.expander(f"{node['subject']}"):
                st.caption(f"Topic: {node['topic']['displayName']} | Votes: {node['upvoteCount']}")
                content = node.get("content", {}).get("data", "")
                st.write(content[:600] + "..." if len(content) > 600 else content)
                
                if st.button("🤖 Get AI Review", key=node["slug"]):
                    with st.spinner("Claude reviewing..."):
                        review = get_ai_review(node["subject"], content)
                        st.markdown(review)
                        
                        if st.button("📋 Copy Reply", key=f"copy_{node['slug']}"):
                            st.code(review, language=None)
                            st.success("Copied!")

st.sidebar.info("Simple review - no confidence yet")
