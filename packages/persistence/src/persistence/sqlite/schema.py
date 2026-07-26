import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    """Initializes the SQLite schema idempotently."""

    # 1. Schema Metadata
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_metadata (
            version INTEGER PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Insert initial version if it doesn't exist
    conn.execute("INSERT OR IGNORE INTO schema_metadata (version) VALUES (1)")

    # 2. Documents
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            checksum TEXT NOT NULL,
            version TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            language TEXT,
            metadata_json TEXT,
            statistics_json TEXT,
            pages_json TEXT NOT NULL
        )
    """)

    # 3. Document Chunks
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            title TEXT,
            page_number INTEGER,
            section_title TEXT,
            created_at TIMESTAMP NOT NULL,
            metadata_json TEXT NOT NULL,
            statistics_json TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id)"
    )

    # 4. Knowledge Concepts
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_concepts (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            concept_type TEXT NOT NULL,
            aliases_json TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TIMESTAMP NOT NULL,
            metadata_json TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
            UNIQUE(document_id, name)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_concepts_document_id ON knowledge_concepts(document_id)"
    )

    # 5. Knowledge Relationships
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_relationships (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            source_concept TEXT NOT NULL,
            target_concept TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TIMESTAMP NOT NULL,
            metadata_json TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY(source_concept) REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
            FOREIGN KEY(target_concept) REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
            UNIQUE(document_id, source_concept, target_concept, relationship_type)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_relationships_document_id "
        "ON knowledge_relationships(document_id)"
    )

    # 5. Learning Content
    conn.execute("""
        CREATE TABLE IF NOT EXISTS learning_content (
            id TEXT PRIMARY KEY,
            source_document_id TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            source_chunk_ids_json TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            statistics_json TEXT NOT NULL,
            FOREIGN KEY(source_document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_learning_document_id "
        "ON learning_content(source_document_id)"
    )
