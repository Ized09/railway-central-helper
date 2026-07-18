import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v1.0 - Split Layout")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Claude Connected")
st.sidebar.warning("⚠️ Always edit before posting")

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

# Left column: Thread list
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Recent Threads")
    if st.button("🔄 Refresh", type="primary", use_container_width=True):
        with st.spinner("Loading..."):
            st.session_state.threads = fetch_threads()
            st.session_state.selected_slug = None

    for edge in st.session_state.get("threads", []):
        node = edge["node"]
        is_bounty = "$" in node["subject"].lower() or "bounty" in node["subject"].lower()
        
        if st.button(f"{'💰 ' if is_bounty else ''}{node['subject'][:60]}...", key=node["slug"], use_container_width=True):
            st.session_state.selected_slug = node["slug"]

# Right column: Review area
with col2:
    if st.session_state.selected_slug:
        selected_node = None
        for edge in st.session_state.get("threads", []):
            if edge["node"]["slug"] == st.session_state.selected_slug:
                selected_node = edge["node"]
                break
        
        if selected_node:
            st.subheader(f"Reviewing: {selected_node['subject']}")
            content = selected_node.get("content", {}).get("data", "")
            st.write(content[:700] + "..." if len(content) > 700 else content)
            
            if st.button("🤖 Generate AI Review + Confidence", type="primary"):
                with st.spinner("Claude reviewing..."):
                    review = get_ai_review(selected_node["slug"], selected_node["subject"], content)
                    st.session_state.current_review = review
                    
                    confidence = 50
                    if "CONFIDENCE:" in review:
                        try:
                            line = [l for l in review.split("\n") if "CONFIDENCE:" in l][0]
                            confidence = int(line.split(":")[1].strip())
                        except:
                            pass
                    
                    st.markdown("### AI Review")
                    st.markdown(review)
                    
                    if confidence >= 80:
                        st.success(f"High Confidence: {confidence}/100")
                    elif confidence >= 60:
                        st.warning(f"Medium Confidence: {confidence}/100")
                    else:
                        st.error(f"Low Confidence: {confidence}/100")
                    
                    if st.button("📋 Copy Review"):
                        st.code(review, language=None)
                        st.success("Copied!")
    else:
        st.info("Select a thread from the left to start reviewing")

st.sidebar.info("Split view - review appears on the right")
