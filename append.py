with open('apps/api/tests/test_analytics.py', 'a', encoding='utf-8') as f:
    f.write('''
def test_analytics_payload_exhaustive_validation(client, auth_headers) -> None:
    # helper to assert 422 or 400
    def assert_invalid(event_type: str, data: dict, expected_msg_fragment: str):
        resp = client.post(
            "/api/v1/analytics/events/batch",
            headers=auth_headers,
            json={
                "events": [{
                    "event_id": "test-id",
                    "event_type": event_type,
                    "resource_id": "doc-1",
                    "idempotency_key": "test-id",
                    "data": data,
                }]
            }
        )
        assert resp.status_code in (400, 422), f"Expected 400/422 for {event_type} {data}, got {resp.status_code} - {resp.text}"
        assert expected_msg_fragment.lower() in resp.text.lower(), f"Expected {expected_msg_fragment} in {resp.text}"

    # chunk_viewed validation
    assert_invalid("chunk_viewed", {}, "section_id")
    assert_invalid("chunk_viewed", {"section_id": None, "chunk_id": "c1"}, "none is not an allowed value")
    assert_invalid("chunk_viewed", {"section_id": "s1", "chunk_id": None}, "none is not an allowed value")
    assert_invalid("chunk_viewed", {"section_id": "s1", "chunk_id": 123}, "string")

    # quiz_completed validation
    assert_invalid("quiz_completed", {}, "score")
    assert_invalid("quiz_completed", {"score": 5}, "total_questions")
    assert_invalid("quiz_completed", {"score": None, "total_questions": 5}, "none is not an allowed value")
    assert_invalid("quiz_completed", {"score": -1, "total_questions": 5}, "greater than or equal to 0")
    assert_invalid("quiz_completed", {"score": 5, "total_questions": -1}, "greater than or equal to 1")
    assert_invalid("quiz_completed", {"score": 6, "total_questions": 5}, "score cannot be greater than total_questions")

    # flashcard_reviewed validation
    assert_invalid("flashcard_reviewed", {}, "card_id")
    assert_invalid("flashcard_reviewed", {"card_id": "c1"}, "difficulty")
    assert_invalid("flashcard_reviewed", {"card_id": None, "difficulty": "easy"}, "none is not an allowed value")
    assert_invalid("flashcard_reviewed", {"card_id": "c1", "difficulty": None}, "none is not an allowed value")
    assert_invalid("flashcard_reviewed", {"card_id": "c1", "difficulty": "invalid_diff"}, "again, hard, good, easy")

    # study_session_completed validation
    assert_invalid("study_session_completed", {}, "completed_at")
    assert_invalid("study_session_completed", {"completed_at": None}, "none is not an allowed value")
    assert_invalid("study_session_completed", {"completed_at": "not-a-timestamp"}, "datetime")
    assert_invalid("study_session_completed", {"completed_at": "2023-01-01T12:00:00"}, "timezone")
''')
