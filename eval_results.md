# Evaluation Results

Tested against a fixed corpus of Stripe API documentation (`payments.md`, `api.md`).

| Question | Result | Notes |
|---|---|---|
| What format does the Stripe API use for responses? | ✅ PASS | Correctly identified JSON, grounded in actual doc content |
| How do I test payments before going live? | ✅ PASS | Correctly found and cited sandbox/testing guidance |
| What is the capital of France? (off-topic control question) | ✅ PASS | Correctly refused to answer — no hallucination, confirms the "I don't have enough information" fallback works as designed |

**Result: 3/3 passed.**

The off-topic question is intentionally included as a negative test — a system that hallucinates an answer here would be failing silently. Passing it is as important as passing the real questions.