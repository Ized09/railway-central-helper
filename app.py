import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.6 - Popup Reviews")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Claude Connected")

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
    prompt = f"""You are a senior Railway engineer.

Thread Title: {thread_subject}

Content: {content[:6000]}

Write a friendly, useful reply."""

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

# Main UI
show_bounties_only = st.checkbox("Show only Bounty threads 💰", value=False)

if st.button("🔄 Refresh Recent Threads", type="primary"):
    with st.spinner("Loading..."):
        threads = fetch_threads()
        
        for edge in threads:
            node = edge["node"]
            is_bounty = "$" in node["subject"].lower() or "bounty" in node["subject"].lower()
            
            if show_bounties_only and not is_bounty:
                continue
                
            with st.expander(f"{'💰 ' if is_bounty else ''}{node['subject']}"):
                st.caption(f"Topic: {node['topic']['displayName']} | Votes: {node['upvoteCount']}")
                content = node.get("content", {}).get("data", "")
                st.write(content[:700] + "..." if len(content) > 700 else content)
                
                if st.button("🤖 Open AI Review", key=node["slug"]):
                    with st.spinner("Claude reviewing..."):
                        review = get_ai_review(node["subject"], content)
                        
                        # Show as popup/dialog
                        with st.dialog("AI Review"):
                            st.markdown(review)
                            if st.button("📋 Copy Reply"):
                                st.code(review, language=None)
                                st.success("Copied!")
                            if st.button("Close"):
                                st.rerun()

st.sidebar.info("Click 'Open AI Review' to see popup")
