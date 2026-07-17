import streamlit as st
import requests

st.set_page_config(page_title="Railway Central Helper", layout="wide")
st.title("🚄 Railway Central Station AI Helper")
st.caption("v0.1 - Click Refresh to load recent threads")

QUERY = """
{
  threads(first: 12, sort: recent_activity) {
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

if st.button("🔄 Refresh Recent Threads"):
    with st.spinner("Loading from Central Station..."):
        threads = fetch_threads()
        for edge in threads:
            node = edge["node"]
            with st.expander(f"**{node['subject']}** - {node['topic']['displayName']}"):
                st.caption(f"Status: {node['status']} | Votes: {node['upvoteCount']}")
                content = node.get("content", {}).get("data", "")[:600]
                st.write(content + "..." if len(content) > 600 else content)

st.info("Prototype ready! Next version will include AI review + suggested replies.")