import streamlit as st
import pandas as pd
from datetime import datetime
from minsearch import Index
import pypdf
import docx

from rag import rag

st.set_page_config(
    page_title="DocuRAG | Internal Knowledge Assistant",
    page_icon="📄",
    layout="centered"
)


def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        reader = pypdf.PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif uploaded_file.name.endswith(".docx"):
        document = docx.Document(uploaded_file)
        return "\n".join(p.text for p in document.paragraphs)
    else:
        return uploaded_file.read().decode("utf-8")


def chunk_text(text, max_chars=1000):
    paragraphs = text.split("\n\n")
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) < max_chars:
            current += p + "\n\n"
        else:
            if current:
                chunks.append(current)
            current = p + "\n\n"
    if current:
        chunks.append(current)
    return chunks


def build_index_from_chunks(chunks, source_name):
    documents = [{"source": source_name, "text": c} for c in chunks]
    index = Index(text_fields=["text"], keyword_fields=["source"])
    index.fit(documents)
    return index


INPUT_RATE = 1.50 / 1_000_000
OUTPUT_RATE = 7.50 / 1_000_000

if "analytics_log" not in st.session_state:
    st.session_state.analytics_log = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "view" not in st.session_state:
    st.session_state.view = "chat"


# --- Sidebar: knowledge base status only ---
with st.sidebar:
    st.header("📚 Knowledge Base")
    if "doc_name" in st.session_state:
        st.success(f"**Active document:**\n{st.session_state.doc_name}")
        st.caption(f"{st.session_state.chunk_count} sections indexed")
        st.caption(f"Loaded at {st.session_state.loaded_at}")
    else:
        st.info("No document loaded yet")
    st.divider()
    st.caption("Powered by Gemini + retrieval-augmented generation")


# --- Top nav: manual toggle instead of st.tabs, so chat_input can pin to bottom ---
nav1, nav2 = st.columns(2)
if nav1.button("💬 Chat", use_container_width=True):
    st.session_state.view = "chat"
if nav2.button("📊 Dashboard", use_container_width=True):
    st.session_state.view = "dashboard"

st.divider()

# ============ CHAT VIEW ============
if st.session_state.view == "chat":
    st.title("📄 DocuRAG")
    st.caption("Ask questions about any internal document — grounded answers, always cited.")

    uploaded_file = st.file_uploader("Upload a document to get started", type=["pdf", "txt", "docx"])

    if uploaded_file:
        if st.session_state.get("doc_name") != uploaded_file.name:
            with st.spinner("Reading and indexing document..."):
                text = extract_text(uploaded_file)
                if not text.strip():
                    st.error("This file doesn't seem to contain readable text.")
                else:
                    chunks = chunk_text(text)
                    index = build_index_from_chunks(chunks, uploaded_file.name)
                    st.session_state.index = index
                    st.session_state.doc_name = uploaded_file.name
                    st.session_state.chunk_count = len(chunks)
                    st.session_state.loaded_at = datetime.now().strftime("%I:%M %p")
                    st.session_state.messages = []

    if "index" in st.session_state:
        st.subheader("💬 Ask a question")

        sample_questions = [
            "Summarize the key points",
            "What are the main requirements?",
            "Are there any deadlines mentioned?",
        ]
        cols = st.columns(len(sample_questions))
        pending_question = None
        for col, q in zip(cols, sample_questions):
            if col.button(q, use_container_width=True):
                pending_question = q

        # show existing conversation so far
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # chat_input at the bottom of the script body (not nested in a container) pins to page bottom
        typed_question = st.chat_input("Type your question here...")
        question = pending_question or typed_question

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        result = rag(question, st.session_state.index, history=st.session_state.messages[:-1])
                    except Exception as e:
                        st.exception(e)
                        result = {"answer": "Something went wrong generating a response. Please try again.",
                                  "input_tokens": 0, "output_tokens": 0, "response_time": 0, "sources": []}
                st.write(result["answer"])
                if result.get("sources"):
                    st.caption(f"📄 Source: {', '.join(result['sources'])}")

            st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

            cost = (result["input_tokens"] * INPUT_RATE) + (result["output_tokens"] * OUTPUT_RATE)
            st.session_state.analytics_log.append({
                "timestamp": datetime.now(),
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "response_time": result["response_time"],
                "cost": cost,
            })

# ============ DASHBOARD VIEW ============
else:
    st.title("📊 Session Dashboard")

    log = st.session_state.analytics_log

    if not log:
        st.info("No conversations yet — ask a question in the Chat view to see analytics here.")
    else:
        df = pd.DataFrame(log)
        total_conversations = len(df)
        avg_response_time = df["response_time"].mean()
        total_cost = df["cost"].sum()
        avg_tokens = (df["input_tokens"] + df["output_tokens"]).mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total conversations", total_conversations)
        col2.metric("Avg response time", f"{avg_response_time:.2f}s")
        col3.metric("Total cost", f"${total_cost:.4f}")
        col4.metric("Avg tokens", f"{avg_tokens:.0f}")

        st.caption("Free tier in use — cost shown is an estimate based on Gemini 3.6 Flash standard paid rates, for reference only.")

        st.divider()
        st.subheader("Cost over time")
        df["cumulative_cost"] = df["cost"].cumsum()
        chart_df = df.set_index("timestamp")[["cumulative_cost"]]
        st.line_chart(chart_df)

        st.divider()
        st.subheader("Response time per query")
        st.bar_chart(df["response_time"])