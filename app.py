import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.2 - AI Review Powered by Claude")

# Load key from Railway Variables (secure)
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("⚠️ Anthropic API key not set. Go to Railway → Variables → Add ANTHROPIC_KEY")
    st.stop()

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
    prompt = f"""You are a helpful senior Railway engineer helping on Central Station.

Thread Title: {thread_subject}
Content: {content[:7000]}

Write a friendly, useful reply that includes:
1. Quick summary of the problem
2. Likely cause
3. Suggested fix or steps
4. Ready-to-post reply (keep it kind and helpful)
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
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"Error calling Claude: {str(e)}"

# Main UI
if st.button("🔄 Refresh Recent Threads"):
    with st.spinner("Loading threads from Central Station..."):
        threads = fetch_threads()
        
        for edge in threads:
            node = edge["node"]
            content_preview = node.get("content", {}).get("data", "")[:500]
            
            with st.expander(f"**{node['subject']}** • {node['topic']['displayName']} • {node['upvoteCount']} votes"):
                st.caption(f"Status: {node['status']} | {node['createdAt'][:10]}")
                st.write(content_preview + "..." if len(content_preview) > 500 else content_preview)
                
                if st.button("🤖 Get AI Review & Suggested Reply", key=node["slug"]):
                    with st.spinner("Claude is thinking..."):
                        review = get_ai_review(node["subject"], node.get("content", {}).get("data", ""))
                        st.markdown("### 🤖 AI Review + Suggested Reply")
                        st.markdown(review)

st.sidebar.success("✅ Using server-side Anthropic key")
st.sidebar.info("Add bounties filter or copy button in next update?")
