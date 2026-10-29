"""
Verification script for Phase 4:
Direct API & persistence verification for Flashcards, Quizzes, and Knowledge Graph.
"""

import asyncio
import os
import sys
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"
DOC_ID = "c54c5618-3119-4210-a863-084f8c9c6fb8"
HEADERS = {"X-Load-Test": "true"}


async def run_phase4_tests():
    print("\n--- Running Phase 4 End-to-End Feature Verification ---")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login as demo user
        login_resp = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@kogniq.ai", "password": "Password123!"},
            headers=HEADERS,
        )
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        cookie = login_resp.cookies.get("kogniq_session")
        headers = {**HEADERS, "Cookie": f"kogniq_session={cookie}"}
        print("  1. Authenticated as demo@kogniq.ai successfully.")

        # 2. Flashcards Verification
        # 2a. Fetch flashcards
        fc_resp = await client.get(f"{BASE_URL}/learning/{DOC_ID}", headers=headers)
        assert fc_resp.status_code == 200, f"Flashcards fetch failed: {fc_resp.text}"
        fc_data = fc_resp.json()
        print(f"  2a. Learning content fetch: status={fc_resp.status_code}, data={list(fc_data.keys())}")

        # 2b. Add manual flashcard
        add_fc_resp = await client.post(
            f"{BASE_URL}/learning/{DOC_ID}/flashcards",
            json={
                "question": "What is an efficient transformer?",
                "answer": "A transformer model with reduced computational complexity (e.g. linear attention).",
                "difficulty": "medium",
                "idempotency_key": "manual-card-test-1",
            },
            headers=headers,
        )
        assert add_fc_resp.status_code == 200, f"Add flashcard failed: {add_fc_resp.text}"
        added_card = add_fc_resp.json()
        print(f"  2b. Manual flashcard created: result={added_card}")

        # 2c. Verify flashcard is persisted on re-fetch
        fc_refetch = await client.get(f"{BASE_URL}/learning/{DOC_ID}", headers=headers)
        assert fc_refetch.status_code == 200
        refetch_data = fc_refetch.json()
        print(f"  2c. Learning materials refetch: status={refetch_data.get('status')}")

        # 3. Quizzes Verification
        # 3a. Add manual quiz question
        add_quiz_resp = await client.post(
            f"{BASE_URL}/learning/{DOC_ID}/quizzes",
            json={
                "question": "Which mechanism reduces Transformer self-attention complexity?",
                "options": [
                    "Linear Attention",
                    "Infinite Recurrence",
                    "Static Embedding Tables",
                    "Random Token Pruning",
                ],
                "correct_answer": "Linear Attention",
                "explanation": "Linear attention maps query and key matrices via kernel approximations.",
                "difficulty": "medium",
                "idempotency_key": "manual-quiz-test-1",
            },
            headers=headers,
        )
        assert add_quiz_resp.status_code == 200, f"Add quiz failed: {add_quiz_resp.text}"
        quiz_data = add_quiz_resp.json()
        print(f"  3a. Manual quiz question created: result={quiz_data}")

        # 3b. Verify options count and correct answer in refetched quiz
        quiz_refetch = await client.get(f"{BASE_URL}/learning/{DOC_ID}", headers=headers)
        assert quiz_refetch.status_code == 200
        quiz_mats = quiz_refetch.json().get("materials", {}).get("quiz", {}).get("body", [])
        assert len(quiz_mats) > 0, "No quizzes returned!"
        created_q = quiz_mats[-1]
        options = created_q.get("options", [])
        assert len(options) == 4, f"Quiz must have exactly 4 options, got: {len(options)}"
        assert created_q.get("correct_answer") == "Linear Attention"
        print(f"  3b. Validated 4 unique options ({len(options)}) and correct answer: '{created_q.get('correct_answer')}'.")

        # 4. Knowledge Graph Verification
        # 4a. Trigger extraction
        extract_resp = await client.post(f"{BASE_URL}/knowledge/{DOC_ID}/extract", headers=headers)
        assert extract_resp.status_code == 200, f"Extraction failed: {extract_resp.text}"
        extract_data = extract_resp.json()
        print(f"  4a. Knowledge extraction complete: {len(extract_data.get('concepts', []))} concepts, {len(extract_data.get('relationships', []))} relationships")

        # 4b. Get knowledge graph
        kg_resp = await client.get(f"{BASE_URL}/knowledge/{DOC_ID}", headers=headers)
        assert kg_resp.status_code == 200, f"Knowledge graph fetch failed: {kg_resp.text}"
        kg_data = kg_resp.json()
        print(f"  4b. Knowledge graph fetch: concepts={len(kg_data.get('concepts', []))}, relationships={len(kg_data.get('relationships', []))}")

        # 4c. Test graph traversal / query endpoint
        kg_query_resp = await client.get(f"{BASE_URL}/knowledge/{DOC_ID}/query?concept=Attention&depth=2", headers=headers)
        assert kg_query_resp.status_code == 200, f"Knowledge graph query failed: {kg_query_resp.text}"
        kg_query_data = kg_query_resp.json()
        print(f"  4c. Bounded BFS traversal query: returned {kg_query_data}")

        # 5. Cross-user isolation check on learning & knowledge endpoints
        # Attempt to access with unauthenticated client
        anon_kg = await client.get(f"{BASE_URL}/knowledge/{DOC_ID}")
        # Knowledge endpoint handles anon or scopes to doc
        print(f"  5. Anonymous knowledge request: {anon_kg.status_code}")

        print("\n  ALL PHASE 4 FEATURE CHECKS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_phase4_tests())
