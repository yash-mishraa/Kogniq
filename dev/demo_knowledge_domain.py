import sys
from pathlib import Path

# Add the source directory to sys.path so the demo can run without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "knowledge" / "src"))

from knowledge import (
    ConceptType,
    KnowledgeConcept,
    KnowledgeGraph,
    KnowledgeMetadata,
    KnowledgeRelationship,
    RelationshipType,
)


def main() -> None:
    print("Initializing Knowledge Domain Demo...\n")

    metadata = KnowledgeMetadata(
        source_document="doc_123",
        source_chunk="chunk_456",
        language="en",
        confidence=0.95,
        extraction_version="1.0.0",
        created_by="demo_script",
    )

    c1 = KnowledgeConcept(
        id="c_machine_learning",
        title="Machine Learning",
        description=(
            "A field of study that gives computers the ability to learn "
            "without being explicitly programmed."
        ),
        concept_type=ConceptType.THEORY,
        aliases=("ML", "Machine learning"),
        metadata=metadata,
    )

    c2 = KnowledgeConcept(
        id="c_neural_network",
        title="Neural Network",
        description=(
            "A series of algorithms that endeavors to recognize underlying "
            "relationships in a set of data."
        ),
        concept_type=ConceptType.ALGORITHM,
        aliases=("NN", "Artificial Neural Network", "ANN"),
        metadata=metadata,
    )

    c3 = KnowledgeConcept(
        id="c_backpropagation",
        title="Backpropagation",
        description="An algorithm used to calculate derivatives quickly.",
        concept_type=ConceptType.ALGORITHM,
        aliases=("Backprop",),
        metadata=metadata,
    )

    r1 = KnowledgeRelationship(
        id="r_1",
        source_concept="c_neural_network",
        target_concept="c_machine_learning",
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.9,
        metadata=metadata,
    )

    r2 = KnowledgeRelationship(
        id="r_2",
        source_concept="c_backpropagation",
        target_concept="c_neural_network",
        relationship_type=RelationshipType.USES,
        confidence=0.99,
        metadata=metadata,
    )

    graph = KnowledgeGraph(
        concepts=(c1, c2, c3),
        relationships=(r1, r2),
    )

    print("--- Knowledge Graph Built Successfully ---\n")
    print(f"Total Concepts: {graph.concept_count}")
    print(f"Total Relationships: {graph.relationship_count}\n")

    print("Concepts:")
    for c in graph.concepts:
        print(f"  - [{c.id}] {c.title} ({c.concept_type.name})")
        print(f"    Aliases: {', '.join(c.aliases) if c.aliases else 'None'}")
        print(f"    Description: {c.description[:50]}...")

    print("\nRelationships:")
    for r in graph.relationships:
        print(
            f"  - [{r.id}] {r.source_concept} --({r.relationship_type.name})--> {r.target_concept}"
        )
        print(f"    Confidence: {r.confidence:.2f}")


if __name__ == "__main__":
    main()
