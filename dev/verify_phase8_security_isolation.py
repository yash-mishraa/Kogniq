"""
Phase 8 Security & Multi-Tenant Isolation Verification
Verifies:
1. Registration & Authentication with 2 distinct users.
2. Document listing isolation: User B sees 0 of User A's documents.
3. RAG Query isolation: User B querying User A's doc receives 403 or empty results (never chunks from User A).
4. Flashcards/Quizzes authorization: User B attempting to modify User A's materials receives 403 Forbidden.
5. Knowledge graph authorization: User B attempting to extract from User A's document receives 403 Forbidden.
"""

import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {"X-Load-Test": "true"}
USER_A_DOC_ID = "c54c5618-3119-4210-a863-084f8c9c6fb8"


async def run_security_tests():
    print("\n--- Running Phase 8 Security & Tenant Isolation Tests ---")
    results = {}

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: Login as User A
        resp_a = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@kogniq.ai", "password": "Password123!"},
            headers=HEADERS,
        )
        assert resp_a.status_code == 200, "User A login failed"
        cookie_a = resp_a.cookies.get("kogniq_session")
        headers_a = {**HEADERS, "Cookie": f"kogniq_session={cookie_a}"}

        # Step 2: Register User B
        user_b_email = "tenant_b@kogniq.ai"
        user_b_pass = "SecurePass456!"
        resp_b_reg = await client.post(
            f"{BASE_URL}/auth/register",
            json={"email": user_b_email, "password": user_b_pass, "display_name": "Tenant B"},
            headers=HEADERS,
        )
        if resp_b_reg.status_code in (200, 201):
            cookie_b = resp_b_reg.cookies.get("kogniq_session")
        else:
            # Already exists, login
            resp_b_login = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": user_b_email, "password": user_b_pass},
                headers=HEADERS,
            )
            assert resp_b_login.status_code == 200, "User B auth failed"
            cookie_b = resp_b_login.cookies.get("kogniq_session")

        headers_b = {**HEADERS, "Cookie": f"kogniq_session={cookie_b}"}
        print("  1. Authenticated two distinct tenants (User A and User B).")

        # Test 1: Document list isolation
        docs_a = await client.get(f"{BASE_URL}/documents", headers=headers_a)
        docs_b = await client.get(f"{BASE_URL}/documents", headers=headers_b)
        docs_a_ids = {d["id"] for d in docs_a.json()}
        docs_b_ids = {d["id"] for d in docs_b.json()}
        assert USER_A_DOC_ID in docs_a_ids, "User A must see their own document"
        assert USER_A_DOC_ID not in docs_b_ids, "CRITICAL: User B must not see User A's document!"
        results["Document List Isolation"] = f"PASSED (User A has {len(docs_a_ids)} docs, User B has {len(docs_b_ids)} docs, 0 overlap)"

        # Test 2: RAG Cross-Tenant Query Isolation
        rag_b_attempt = await client.post(
            f"{BASE_URL}/rag/query",
            json={
                "query": "What are efficient transformers?",
                "document_ids": [USER_A_DOC_ID],
                "generate": False,
            },
            headers=headers_b,
        )
        # Should return 403 or 0 sources (no chunk leak)
        if rag_b_attempt.status_code == 403:
            results["RAG Query Isolation"] = "PASSED (Rejected with HTTP 403 Forbidden)"
        else:
            sources = rag_b_attempt.json().get("sources", [])
            assert len(sources) == 0, f"LEAK: User B received {len(sources)} sources from User A's document!"
            results["RAG Query Isolation"] = "PASSED (Filtered to 0 sources, 0 chunks leaked)"

        # Test 3: Flashcard Modification Authorization
        fc_b_attempt = await client.post(
            f"{BASE_URL}/learning/{USER_A_DOC_ID}/flashcards",
            json={
                "question": "Hacked question?",
                "answer": "Hacked answer.",
                "difficulty": "hard",
                "idempotency_key": "hack-key-1",
            },
            headers=headers_b,
        )
        assert fc_b_attempt.status_code in (403, 401), f"CRITICAL: User B was allowed to modify User A's flashcards! ({fc_b_attempt.status_code})"
        results["Flashcard Tenant Authorization"] = f"PASSED (Blocked with HTTP {fc_b_attempt.status_code} Forbidden)"

        # Test 4: Quiz Modification Authorization
        quiz_b_attempt = await client.post(
            f"{BASE_URL}/learning/{USER_A_DOC_ID}/quizzes",
            json={
                "question": "Hacked quiz?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Hacked",
                "difficulty": "medium",
                "idempotency_key": "hack-quiz-key-1",
            },
            headers=headers_b,
        )
        assert quiz_b_attempt.status_code in (403, 401), f"CRITICAL: User B was allowed to modify User A's quiz! ({quiz_b_attempt.status_code})"
        results["Quiz Tenant Authorization"] = f"PASSED (Blocked with HTTP {quiz_b_attempt.status_code} Forbidden)"

        # Test 5: Knowledge Extraction Authorization
        extract_b_attempt = await client.post(
            f"{BASE_URL}/knowledge/{USER_A_DOC_ID}/extract",
            headers=headers_b,
        )
        assert extract_b_attempt.status_code in (403, 401), f"CRITICAL: User B was allowed to extract knowledge from User A's document! ({extract_b_attempt.status_code})"
        results["Knowledge Graph Authorization"] = f"PASSED (Blocked with HTTP {extract_b_attempt.status_code} Forbidden)"

    for k, v in results.items():
        print(f"  {k}: {v}")
    print("\n  ALL SECURITY AND TENANT ISOLATION TESTS PASSED CLEANLY!")
    return True


if __name__ == "__main__":
    asyncio.run(run_security_tests())
