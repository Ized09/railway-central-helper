import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v1.2 - Fable 5 Fixed")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

st.sidebar.success("✅ Claude Connected (Fable 5)")
st.sidebar.warning("⚠️ Always manually edit before posting")

tab1, tab2 = st.tabs(["📋 Thread Helper", "✍️ Humanizer"])

# ====================== THREAD HELPER ======================
with tab1:
    if "threads" not in st.session_state:
        st.session_state.threads = []
    if "selected_slug" not in st.session_state:
        st.session_state.selected_slug = None

    if st.button("🔄 Refresh Recent Threads", type="primary"):
        with st.spinner("Loading..."):
            try:
                resp = requests.post("https://station-server.railway.com/gql", json={"query": """
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
                """})
                st.session_state.threads = resp.json()["data"]["threads"]["edges"]
                st.session_state.selected_slug = None
            except Exception as e:
                st.error(f"Fetch error: {e}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Recent Threads")
        for edge in st.session_state.threads:
            node = edge["node"]
            is_bounty = "$" in node["subject"].lower() or "bounty" in node["subject"].lower()
            if st.button(f"{'💰 ' if is_bounty else ''}{node['subject'][:70]}...", key=node["slug"], use_container_width=True):
                st.session_state.selected_slug = node["slug"]

    with col2:
        if st.session_state.selected_slug:
            # Find selected thread
            selected_node = next((edge["node"] for edge in st.session_state.threads if edge["node"]["slug"] == st.session_state.selected_slug), None)
            if selected_node:
                st.subheader(f"Reviewing: {selected_node['subject']}")
                content = selected_node.get("content", {}).get("data", "")
                st.write(content[:700] + "..." if len(content) > 700 else content)
                
                if st.button("🤖 Generate with Fable 5", type="primary"):
                    with st.spinner("Fable 5 thinking..."):
                        prompt = f"""You are a senior Railway engineer.\n\nThread Title: {selected_node['subject']}\n\nContent: {content[:6000]}\n\nWrite a friendly, useful reply."""
                        try:
                            resp = requests.post(
                                "https://api.anthropic.com/v1/messages",
                                headers={
                                    "x-api-key": ANTHROPIC_KEY,
                                    "anthropic-version": "2023-06-01",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "model": "claude-fable-5",
                                    "max_tokens": 1200,
                                    "messages": [{"role": "user", "content": prompt}]
                                }
                            )
                            data = resp.json()
                            if "content" in data and len(data["content"]) > 0:
                                review = data["content"][0]["text"]
                                st.markdown(review)
                                if st.button("📋 Copy"):
                                    st.code(review, language=None)
                                    st.success("Copied!")
                            else:
                                st.error(f"Unexpected response: {data}")
                        except Exception as e:
                            st.error(f"API Error: {str(e)}")
        else:
            st.info("← Select a thread from the left")

# ====================== HUMANIZER ======================
with tab2:
    st.subheader("✍️ Humanizer (Fable 5)")
    ai_text = st.text_area("Paste AI-generated text here:", height=250)
    
    if st.button("✨ Humanize with Fable 5", type="primary"):
        if ai_text.strip():
            with st.spinner("Humanizing..."):
                prompt = f"""Rewrite this to sound like a real helpful human on Railway Central Station. Natural, friendly, not robotic.

Original:
{ai_text}"""

                try:
                    resp = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": ANTHROPIC_KEY,
                            "anthropic-version": "2023-06-01",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "claude-fable-5",
                            "max_tokens": 1200,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    data = resp.json()
                    if "content" in data and len(data["content"]) > 0:
                        humanized = data["content"][0]["text"]
                        st.session_state.humanized = humanized
                        st.success("Done!")
                    else:
                        st.error(f"API response error: {data}")
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")
        else:
            st.warning("Please paste some text first.")

    if "humanized" in st.session_state:
        st.subheader("Humanized Version")
        st.markdown(st.session_state.humanized)
        
        if st.button("📋 Copy Humanized"):
            st.code(st.session_state.humanized, language=None)
            st.success("Copied!")

st.sidebar.info("Fable 5 is more creative - good for humanizing")
