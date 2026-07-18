import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.2 - AI Review Powered by Claude")

ANTHROPIC_KEY = st.sidebar.text_input("Anthropic API Key", type="password", value=os.getenv("ANTHROPIC_KEY", ""))

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
    if not ANTHROPIC_KEY:
        return "Please add your Anthropic API key in the sidebar."
    
    prompt = f"""You are a helpful senior Railway engineer on Central Station.
Review this thread and write a friendly, useful reply.

Thread Title: {thread_subject}
Content: {content[:8000]}

Provide:
1. Quick summary of the issue
2. Likely cause
3. Suggested fix or troubleshooting steps
4. A ready-to-post reply (keep it helpful and concise)
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
if st.button("🔄 Refresh Recent Threads"):
    with st.spinner("Loading threads..."):
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
                        st.markdown("### AI Review + Suggested Reply")
                        st.markdown(review)

st.sidebar.info("Add your Anthropic key to enable AI reviews.")
