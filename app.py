import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.8 - Review Below Thread")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Claude Connected")

# Session state
if "selected_slug" not in st.session_state:
    st.session_state.selected_slug = None
if "reviews" not in st.session_state:
    st.session_state.reviews = {}

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

def get_ai_review(thread_slug, thread_subject, content):
    if thread_slug in st.session_state.reviews:
        return st.session_state.reviews[thread_slug]
    
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
        review = resp.json()["content"][0]["text"]
        st.session_state.reviews[thread_slug] = review
        return review
    except Exception as e:
        return f"Error: {str(e)}"

# Refresh
if st.button("🔄 Refresh Recent Threads", type="primary"):
    with st.spinner("Loading..."):
        st.session_state.threads = fetch_threads()
        st.session_state.selected_slug = None

# Display threads
st.subheader("Recent Threads")
for edge in st.session_state.get("threads", []):
    node = edge["node"]
    is_bounty = "$" in node["subject"].lower() or "bounty" in node["subject"].lower()
    
    col1, col2 = st.columns([5,1])
    with col1:
        if st.button(f"{'💰 ' if is_bounty else ''}{node['subject']}", key=node["slug"]):
            st.session_state.selected_slug = node["slug"]
    with col2:
        st.caption(node['topic']['displayName'])

# Show review immediately below selected thread
if st.session_state.selected_slug:
    selected_node = None
    for edge in st.session_state.get("threads", []):
        if edge["node"]["slug"] == st.session_state.selected_slug:
            selected_node = edge["node"]
            break
    
    if selected_node:
        st.divider()
        st.subheader(f"Reviewing: {selected_node['subject']}")
        content = selected_node.get("content", {}).get("data", "")
        st.write(content[:800] + "..." if len(content) > 800 else content)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generate AI Review", type="primary"):
                with st.spinner("Claude reviewing..."):
                    review = get_ai_review(selected_node["slug"], selected_node["subject"], content)
                    st.session_state.current_review = review
        with col2:
            if st.button("📋 Copy Review"):
                if "current_review" in st.session_state:
                    st.code(st.session_state.current_review, language=None)
                    st.success("Copied!")

        if "current_review" in st.session_state:
            st.markdown("### AI Review")
            st.markdown(st.session_state.current_review)

st.sidebar.info("1. Refresh\n2. Click thread title\n3. Generate AI Review")
