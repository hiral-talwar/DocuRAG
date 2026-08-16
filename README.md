# DocuRAG

**DocuRAG** is a retrieval-augmented generation (RAG) assistant that lets you upload any document — PDF, Word, or text — and ask questions about it in a chat interface. Answers are generated using only the content actually retrieved from your document, with source citations, instead of relying on the AI's general knowledge or risking hallucination.

🚀 **Live App:** https://docurag-kig5.onrender.com

*(Free-tier hosting — the app may take 30-60 seconds to wake up if it's been idle.)*

---

## ✨ Key Features

- **General Document Upload:** Works with any PDF, DOCX, or TXT file — not limited to a single hardcoded dataset.
- **Grounded, Cited Answers:** Every answer is generated strictly from retrieved document content, with the source file shown alongside the response.
- **Anti-Hallucination Safeguard:** Explicitly instructed to say "I don't have enough information" when the answer isn't in the document, verified through testing.
- **Conversational Memory:** Follow-up questions correctly reference prior context within the same session.
- **Usage Analytics Dashboard:** Tracks total conversations, average response time, estimated cost, and token usage, with live charts.
- **Resilient by Design:** Automatic retry logic and graceful fallback messaging for transient API failures or rate limits.

---

## 🛠 Tech Stack

| Category | Tools |
|---|---|
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) |
| **LLM** | ![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=flat&logo=googlegemini&logoColor=white) |
| **Retrieval** | ![Python](https://img.shields.io/badge/minsearch-3776AB?style=flat&logo=python&logoColor=white) |
| **Data Processing** | ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white) |
| **File Parsing** | ![PDF](https://img.shields.io/badge/pypdf-EE4C2C?style=flat) ![DOCX](https://img.shields.io/badge/python--docx-2B579A?style=flat) |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat&logo=render&logoColor=white) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- A [Gemini API key](https://aistudio.google.com/) (free tier available)

### Installation & Launch

1. **Clone the Repo**

```
git clone https://github.com/hiral-talwar/DocuRAG.git
cd DocuRAG
```

2. **Install Dependencies**

```
pip install -r requirements.txt
```

3. **Add your API key**

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your-api-key-here
```

4. **Launch the App**

```
streamlit run app.py
```

---

## 📊 How It Works

DocuRAG follows a standard retrieval-augmented generation pipeline:

1. **Text Extraction:** Uploaded PDF, DOCX, or TXT files are parsed and converted to plain text.
2. **Chunking:** Long documents are split into smaller, paragraph-aware chunks (~1000 characters) to improve search relevance.
3. **Indexing:** Chunks are indexed using `minsearch` for fast keyword-based retrieval.
4. **Retrieval:** For each question, the top 3 most relevant chunks are retrieved — recent conversation history is folded into the search query to support follow-up questions.
5. **Generation:** Retrieved chunks, conversation history, and the question are combined into a strict prompt sent to Gemini, which is instructed to answer only from the provided context.
6. **Citation & Logging:** The response is shown with its source file, and token usage, cost, and response time are logged for the analytics dashboard.

---

## 📁 Repository Highlights

- `app.py`: The Streamlit application — chat UI, file upload, and analytics dashboard.
- `rag.py`: Core RAG pipeline — retrieval, prompt construction, and the Gemini API call with retry logic.
- `ingest.py`: Document loading and search index construction for the fixed evaluation corpus.
- `evaluate.py`: Evaluation script — runs a fixed set of test questions (including a deliberate off-topic control question) against known documents.
- `Dockerfile`: Container definition used for deployment on Render.
- `eval_results.md`: Output of the evaluation run.

---

## 🎯 Design Decisions

- Chunk size was set to ~1000 characters to balance retrieval relevance against providing enough context per chunk.
- Source citations were added because ungrounded answers are especially risky for reference/policy-style documents — trust requires traceability.
- An explicit "I don't have enough information" instruction was added after testing showed this was necessary to prevent hallucination on unanswerable questions.
- Retry logic with exponential backoff was added after encountering transient API failures during development.
- Evaluated against a fixed, known test corpus (rather than only ad hoc testing) to produce a measurable, defensible accuracy claim.

## 🔭 Limitations / What I'd Improve

- No reranking step — retrieval is single-pass keyword search rather than hybrid or semantic search.
- No persistent storage — documents and conversations reset when the session ends.
- Evaluation set is intentionally small; a production system would need a larger, continuously updated test set.

---

MIT License © 2026
