import os
from minsearch import Index

def load_documents(docs_folder="docs"):
    documents = []
    for filename in os.listdir(docs_folder):
        filepath = os.path.join(docs_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        documents.append({
            "source": filename,
            "text": text
        })
    return documents

def build_index(documents):
    index = Index(
        text_fields=["text"],
        keyword_fields=["source"]
    )
    index.fit(documents)
    return index
if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    index = build_index(docs)
    results = index.search("how do I create a payment intent?", num_results=3)
    for r in results:
        print(r["source"])