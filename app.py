import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.4 - Bounty Focus + Copy Button")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set in Railway Variables.")
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
- Quick summary of the problem
- Likely cause
- Suggested fix or steps
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
        return f"Error calling Claude: {str(e)}"

# UI
show_bounties_only = st.checkbox("Show only Bounty threads 💰", value=True)

if st.button("🔄 Refresh Recent Threads", type="primary"):
    with st.spinner("Loading from Central Station..."):
        threads = fetch_threads()
        
        for edge in threads:
            node = edge["node"]
            subject_lower = node["subject"].lower()
            is_bounty = "$" in subject_lower or "bounty" in subject_lower
            
            if show_bounties_only and not is_bounty:
                continue
                
            with st.expander(f"{'💰 ' if is_bounty else ''}{node['subject']} • {node['topic']['displayName']}"):
                st.caption(f"Status: {node['status']} | Votes: {node['upvoteCount']}")
                content = node.get("content", {}).get("data", "")
                st.write(content[:700] + "..." if len(content) > 700 else content)
                
                if st.button("🤖 Get AI Review", key=node["slug"]):
                    with st.spinner("Claude is thinking..."):
                        review = get_ai_review(node["subject"], content)
                        st.markdown("### 🤖 AI Review")
                        st.markdown(review)
                        
                        if st.button("📋 Copy Reply", key=f"copy_{node['slug']}"):
                            st.code(review, language=None)
                            st.success("✅ Copied to clipboard! Paste it in Central Station.")

st.sidebar.success("✅ Ready for bounties")
