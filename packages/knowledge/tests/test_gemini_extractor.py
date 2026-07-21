import pytest
from knowledge.extractors.gemini.exceptions import GeminiParsingError
from knowledge.extractors.gemini.parser import GeminiResponseParser


def test_parser_successful_extraction() -> None:
    parser = GeminiResponseParser()
    json_response = """
    {
      "concepts": [
        {"id": "c1", "title": "Concept One", "aliases": ["one"]},
        {"id": "c2", "title": "Concept Two", "aliases": []}
      ],
      "relationships": [
        {"source": "c1", "target": "c2", "type": "RELATED_TO"}
      ]
    }
    """
    graph = parser.parse(json_response)

    assert graph.concept_count == 2
    assert graph.relationship_count == 1

    c1 = next(c for c in graph.concepts if c.id == "c1")
    assert c1.title == "Concept One"
    assert c1.aliases == ("one",)


def test_parser_ignores_duplicates() -> None:
    parser = GeminiResponseParser()
    json_response = """
    {
      "concepts": [
        {"id": "c1", "title": "Concept One"},
        {"id": "c1", "title": "Concept One Again"},
        {"id": "c2", "title": "Concept Two"}
      ],
      "relationships": [
        {"source": "c1", "target": "c2", "type": "RELATED_TO"},
        {"source": "c1", "target": "c2", "type": "RELATED_TO"}
      ]
    }
    """
    graph = parser.parse(json_response)

    # Should keep only the first instance of c1, plus c2
    assert graph.concept_count == 2
    assert graph.concepts[0].title == "Concept One"
    assert graph.concepts[1].title == "Concept Two"

    # Should keep only the first relationship
    assert graph.relationship_count == 1


def test_parser_malformed_json_raises_error() -> None:
    parser = GeminiResponseParser()
    json_response = "{ malformed json "

    with pytest.raises(GeminiParsingError):
        parser.parse(json_response)


def test_parser_invalid_schema() -> None:
    parser = GeminiResponseParser()
    json_response = """
    {
      "not_concepts": []
    }
    """
    # Should not crash, just return empty graph
    graph = parser.parse(json_response)
    assert graph.concept_count == 0
    assert graph.relationship_count == 0


def test_parser_empty_response() -> None:
    parser = GeminiResponseParser()
    json_response = "{}"

    graph = parser.parse(json_response)
    assert graph.concept_count == 0
    assert graph.relationship_count == 0


def test_parser_strips_markdown() -> None:
    parser = GeminiResponseParser()
    json_response = '```json\n{"concepts": [{"id": "c1", "title": "C1"}]}\n```'

    graph = parser.parse(json_response)
    assert graph.concept_count == 1
    assert graph.concepts[0].id == "c1"


def test_parser_ignores_invalid_relationships() -> None:
    parser = GeminiResponseParser()
    json_response = """
    {
      "concepts": [
        {"id": "c1", "title": "C1"}
      ],
      "relationships": [
        {"source": "c1", "target": "c2", "type": "RELATED_TO"}
      ]
    }
    """
    graph = parser.parse(json_response)

    # c2 doesn't exist in concepts, so relationship should be ignored
    assert graph.concept_count == 1
    assert graph.relationship_count == 0
