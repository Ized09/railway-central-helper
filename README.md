# 🚄 Railway Central Station AI Helper

A Streamlit app that pulls recent threads from Railway's community forum and uses Claude to draft helpful, engineer-style replies — so you can triage and respond to community questions faster.

## What it does

- Fetches the 20 most recent threads from Railway's community GraphQL endpoint
- Lets you filter to just bounty/paid threads with one click
- Shows a preview of each thread's content in an expandable card
- Generates an AI-drafted reply for any thread on demand, written in the voice of a senior Railway engineer
- Caches generated reviews per-session so you don't burn API calls re-generating the same reply
- Lets you pull up a review in a copyable code block

## Requirements

- Python 3.9+
- An Anthropic API key with access to Claude

## Setup

1. Clone the repo and install dependencies:

   ```bash
   pip install streamlit requests
   ```

2. Set your Anthropic API key as an environment variable:

   ```bash
   export ANTHROPIC_KEY="your-api-key-here"
   ```

3. Run the app:

   ```bash
   streamlit run railway_helper.py
   ```

## Usage

1. Click **🔄 Refresh Recent Threads** to load the latest threads.
2. Optionally check **Show only Bounty threads 💰** to filter to threads mentioning bounties or "$".
3. Expand any thread to read its content.
4. Click **🤖 Get AI Review** to generate a suggested reply with Claude.
5. Click **📋 Show for Copy** to display the generated reply in a plain-text code block for easy copying.

## Notes

- Reviews are cached only for the current session (`st.session_state`) — refreshing the browser tab clears them.
- Thread data is only refetched when you explicitly click **Refresh Recent Threads**; otherwise the app reuses what's already loaded, so switching the bounty filter or generating reviews won't reset your view.
- Network calls (to the Railway GraphQL endpoint and the Anthropic API) use explicit timeouts and surface errors in the UI rather than failing silently.

## Known limitations

- The "Copy" button doesn't use the system clipboard (Streamlit has no native clipboard API) — it displays the text in a code block for manual copy.
- No pagination beyond the first 20 threads.
- No persistence across sessions or users; this is a single-session helper tool, not a multi-user dashboard.
