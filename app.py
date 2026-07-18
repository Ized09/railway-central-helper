import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.5 - Confidence Scoring Fixed")

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

def get_ai_review_with_confidence(thread_subject, content):
    prompt = f"""You are a senior Railway engineer.

Thread: {thread_subject}

Content: {content[:7000]}

Write a helpful reply.

At the very end, add exactly these two lines:
CONFIDENCE_SCORE: [a number between 0 and 100]
CONFIDENCE_REASON: [one short sentence]"""

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
                "max_tokens": 1600,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return resp.json()["content"][0]["text"]
    except Exception as e:
        return f"API Error: {str(e)}"

# Main UI
show_bounties_only = st.checkbox("Show only Bounty threads 💰", value=False)

if st.button("🔄 Refresh Recent Threads", type="primary"):
    with st.spinner("Loading threads..."):
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
                
                if st.button("🤖 Get AI Review + Confidence", key=node["slug"]):
                    with st.spinner("Claude is reviewing..."):
                        review = get_ai_review_with_confidence(node["subject"], content)
                        st.markdown(review)
                        
                        # Try to extract confidence
                        confidence = None
                        reason = ""
                        if "CONFIDENCE_SCORE:" in review:
                            try:
                                lines = review.split("\n")
                                for line in lines:
                                    if "CONFIDENCE_SCORE:" in line:
                                        confidence = int(line.split(":")[1].strip())
                                    if "CONFIDENCE_REASON:" in line:
                                        reason = line.split(":", 1)[1].strip()
                            except:
                                pass
                        
                        if confidence is not None:
                            if confidence >= 80:
                                st.success(f"High Confidence: {confidence}/100")
                            elif confidence >= 60:
                                st.warning(f"Medium Confidence: {confidence}/100")
                            else:
                                st.error(f"Low Confidence: {confidence}/100")
                            if reason:
                                st.caption(f"Reason: {reason}")
                        
                        if st.button("📋 Copy Reply", key=f"copy_{node['slug']}"):
                            st.code(review, language=None)
                            st.success("Copied!")

st.sidebar.success("✅ Confidence scoring active")
