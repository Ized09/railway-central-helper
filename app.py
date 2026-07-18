import streamlit as st
import requests
import os

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v1.4 - Final Polished")

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

if not ANTHROPIC_KEY:
    st.error("Anthropic API key not set.")
    st.stop()

# Model toggle
model_options = {
    "Fable 5 (Creative & Human-like)": "claude-fable-5",
    "Sonnet 5 (Fast & Reliable)": "claude-sonnet-5"
}
selected_model_name = st.sidebar.selectbox("AI Model", list(model_options.keys()))
selected_model = model_options[selected_model_name]

st.sidebar.success(f"✅ {selected_model_name}")
st.sidebar.warning("⚠️ Always manually edit before posting")

tab1, tab2 = st.tabs(["📋 Thread Helper", "✍️ Humanizer"])

# ====================== THREAD HELPER ======================
with tab1:
    if "threads" not in st.session_state:
        st.session_state.threads = []
    if "selected_slug" not in st.session_state:
        st.session_state.selected_slug = None

    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("🔄 Refresh Threads", type="primary", use_container_width=True):
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
                except:
                    st.error("Could not fetch threads")

        st.subheader("Recent Threads")
        for edge in st.session_state.threads:
            node = edge["node"]
            is_bounty = "$" in node["subject"].lower() or "bounty" in node["subject"].lower()
            if st.button(f"{'💰 ' if is_bounty else ''}{node['subject'][:70]}...", key=node["slug"], use_container_width=True):
                st.session_state.selected_slug = node["slug"]

    with col2:
        if st.session_state.selected_slug:
            selected_node = next((e["node"] for e in st.session_state.threads if e["node"]["slug"] == st.session_state.selected_slug), None)
            if selected_node:
                st.subheader(f"Reviewing: {selected_node['subject']}")
                content = selected_node.get("content", {}).get("data", "")
                st.write(content[:700] + "..." if len(content) > 700 else content)
                
                if st.button(f"🤖 Generate Review ({selected_model_name.split(' ')[0]})", type="primary"):
                    with st.spinner(f"Generating with {selected_model_name}..."):
                        prompt = f"""You are a senior Railway engineer.

Thread Title: {selected_node['subject']}

Content: {content[:6000]}

Write a friendly, useful reply."""

                        resp = requests.post(
                            "https://api.anthropic.com/v1/messages",
                            headers={
                                "x-api-key": ANTHROPIC_KEY,
                                "anthropic-version": "2023-06-01",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": selected_model,
                                "max_tokens": 1200,
                                "messages": [{"role": "user", "content": prompt}]
                            },
                            timeout=60
                        )
                        review = resp.json()["content"][0]["text"] if "content" in resp.json() else "Error getting response"
                        st.markdown(review)
                        
                        if st.button("📋 Copy"):
                            st.code(review, language=None)
                            st.success("Copied!")
        else:
            st.info("Select a thread from the left panel")

# ====================== HUMANIZER ======================
with tab2:
    st.subheader(f"✍️ Humanizer ({selected_model_name})")
    ai_text = st.text_area("Paste AI text here:", height=250)
    
    if st.button("✨ Humanize", type="primary"):
        if ai_text.strip():
            with st.spinner(f"Humanizing with {selected_model_name}..."):
                prompt = f"""Rewrite this to sound like a real helpful human on Railway Central Station. Natural and friendly.

Original:
{ai_text}"""

                resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": ANTHROPIC_KEY,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": selected_model,
                        "max_tokens": 1200,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=60
                )
                humanized = resp.json()["content"][0]["text"] if "content" in resp.json() else "Error"
                st.markdown(humanized)
                
                if st.button("📋 Copy"):
                    st.code(humanized, language=None)
                    st.success("Copied!")
        else:
            st.warning("Paste text first.")

st.sidebar.info("Toggle model in sidebar")
