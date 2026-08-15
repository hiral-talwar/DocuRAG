import os
import time
from dotenv import load_dotenv
from google import genai
from ingest import load_documents, build_index

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def build_context(search_results):
    context_parts = []
    for r in search_results:
        context_parts.append(f"Source: {r['source']}\n{r['text']}")
    return "\n\n".join(context_parts)


def rag(question, index, history=None):
    history = history or []

    recent_context = " ".join(h["content"] for h in history[-4:])
    search_query = f"{recent_context} {question}".strip()

    search_results = index.search(search_query, num_results=3)
    context = build_context(search_results)
    sources = list(set(r["source"] for r in search_results))

    history_text = ""
    if history:
        history_text = "PREVIOUS CONVERSATION:\n"
        for h in history[-4:]:
            history_text += f"{h['role'].upper()}: {h['content']}\n"
        history_text += "\n"

    prompt = f"""
You are an assistant answering questions using only the provided context.
Use the previous conversation only to understand what the user is referring to
(e.g. pronouns or follow-ups) — but still answer strictly using the CONTEXT below.
If the context does not contain enough information to answer, say
"I don't have enough information in these documents to answer that."

{history_text}CONTEXT:
{context}

QUESTION: {question}

ANSWER:
""".strip()

    start_time = time.time()

    for attempt in range(3):
        try:
            response = client.models.generate_content(
               model="gemini-3.5-flash-lite",
                contents=prompt
            )
            elapsed = time.time() - start_time
            usage = response.usage_metadata
            return {
                "answer": response.text,
                "input_tokens": usage.prompt_token_count,
                "output_tokens": usage.candidates_token_count,
                "response_time": elapsed,
                "sources": sources,
            }
        except Exception as e:
            print(f"--- Gemini API error (attempt {attempt+1}) ---")
            print(e)
            if attempt < 2:
                time.sleep(2)
            else:
                elapsed = time.time() - start_time
                return {
                    "answer": "Sorry, the AI service is temporarily unavailable. Please try asking your question again in a moment.",
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "response_time": elapsed,
                    "sources": [],
                }

if __name__ == "__main__":
    docs = load_documents()
    index = build_index(docs)

    question = "How do I create a payment intent?"
    result = rag(question, index)
    print(result["answer"])
    print(f"Tokens: {result['input_tokens']} in / {result['output_tokens']} out")
    print(f"Time: {result['response_time']:.2f}s")