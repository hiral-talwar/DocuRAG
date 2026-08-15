from ingest import load_documents, build_index
from rag import rag

TEST_QUESTIONS = [
    {"question": "What format does the Stripe API use for responses?", "expect_keyword": "JSON"},
    {"question": "How do I test payments before going live?", "expect_keyword": "test"},
    {"question": "What is the capital of France?", "expect_keyword": "don't have enough information"},
]

def run_evaluation():
    docs = load_documents()
    index = build_index(docs)

    results = []
    for test in TEST_QUESTIONS:
        result = rag(test["question"], index)
        answer = result["answer"]
        passed = test["expect_keyword"].lower() in answer.lower()
        results.append({
            "question": test["question"],
            "passed": passed,
            "answer": answer,
        })

    passed_count = sum(1 for r in results if r["passed"])
    print(f"\n{'='*50}")
    print(f"RESULTS: {passed_count}/{len(results)} passed")
    print(f"{'='*50}\n")

    for r in results:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"{status} | {r['question']}")
        print(f"   Answer: {r['answer'][:150]}")
        print()

    return results


if __name__ == "__main__":
    run_evaluation()