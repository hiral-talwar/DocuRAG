import os
from dotenv import load_dotenv
from google import genai
from ingest import load_documents, build_index

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """
You are an assistant answering questions using only the provided context.
If the context does not contain enough information to answer, say
"I don't have enough information in these documents to answer that."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:
""".strip()

def build_context(search_results):
    context_parts = []
    for r in search_results:
        context_parts.append(f"Source: {r['source']}\n{r['text']}")
    return "\n\n".join(context_parts)

def rag(question, index):
    search_results = index.search(question, num_results=3)
    context = build_context(search_results)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text
if __name__ == "__main__":
    docs = load_documents()
    index = build_index(docs)

    question = "How do I create a payment intent?"
    
    # DEBUG: see what search actually found
    search_results = index.search(question, num_results=3)
    print("--- SEARCH RESULTS ---")
    for r in search_results:
        print(r["source"])
    print("----------------------")

    answer = rag(question, index)
    print(answer)