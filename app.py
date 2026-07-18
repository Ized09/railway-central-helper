import streamlit as st
import requests
import os
import json

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.5 - Confidence Scoring Added")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not found. Add it in Railway Variables as ANTHROPIC_KEY")
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
        st.error("Could not fetch threads from Central Station")
        return []

def get_ai_review_with_confidence(thread_subject, content):
    prompt = f"""You are a senior Railway engineer helping on Central Station.

Thread Title: {thread_subject}
Content: {content[:7000]}

Please do the following:
1. Write a friendly, helpful, and accurate reply.
2. At the end, add this exact format on a new line:
CONFIDENCE: [number from 0 to 100]
REASONING: [one short sentence explaining your confidence]

Only output the reply + the two lines above. Do not add extra text.
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
                "max_tokens": 1600,
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        text = resp.json()["content"][0]["text"]
        return text
    except Exception as e:
        return f"Error: {str(e)}"

# UI
show_bounties_only = st.checkbox("Show only Bounty threads 💰", value=False)

if st.button("🔄 Refresh Recent Threads", type="primary"):
    with st.spinner("Loading threads..."):
        threads = fetch_threads()
        
        for edge in threads:
            node = edge["node"]
            is_bounty = "$" in node["subject"].lower() or "bounty" in node["subject"].lower()
            
            if show_bounties_only and not is_bounty:
                continue
                
            with st.expander(f"{'💰 ' if is_bounty else ''}{node['subject']} • {node['topic']['displayName']}"):
                st.caption(f"Status: {node['status']} | Votes: {node['upvoteCount']}")
                content = node.get("content", {}).get("data", "")
                st.write(content[:650] + "..." if len(content) > 650 else content)
                
                if st.button("🤖 Get AI Review + Confidence", key=node["slug"]):
                    with st.spinner("Claude is reviewing..."):
                        review = get_ai_review_with_confidence(node["subject"], content)
                        
                        # Try to extract confidence
                        confidence = None
                        if "CONFIDENCE:" in review:
                            try:
                                conf_line = [line for line in review.split("\n") if "CONFIDENCE:" in line][0]
                                confidence = int(conf_line.split(":")[1].strip())
                            except:
                                pass
                        
                        st.markdown("### 🤖 AI Review + Suggested Reply")
                        st.markdown(review)
                        
                        if confidence is not None:
                            if confidence >= 80:
                                st.success(f"✅ High Confidence: {confidence}/100")
                            elif confidence >= 60:
                                st.warning(f"⚠️ Medium Confidence: {confidence}/100")
                            else:
                                st.error(f"❌ Low Confidence: {confidence}/100")
                        
                        if st.button("📋 Copy Reply", key=f"copy_{node['slug']}"):
                            st.code(review, language=None)
                            st.success("Reply copied! You can paste it in Central Station.")

st.sidebar.success("✅ v0.5 - Confidence Scoring Active")
st.sidebar.info("Next: Slack notifications (when ready)")
