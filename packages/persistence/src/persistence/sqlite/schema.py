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
    # Create Knowledge States table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge_states (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            mastery_score REAL NOT NULL,
            last_reviewed_at TEXT,
            next_review_due TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_states_user_resource ON knowledge_states(user_id, resource_id)
        """
    )

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
    # Migration for Phase III: user_id for ownership
    try:
        conn.execute("ALTER TABLE documents ADD COLUMN user_id TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)")
    except sqlite3.OperationalError:
        pass

    # Migration for Stage 4: Content Intelligence
    def add_column(table: str, column_def: str) -> None:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                pass
            else:
                raise e

    add_column("documents", "resource_type TEXT")
    add_column("documents", "status TEXT")
    add_column("documents", "updated_at TIMESTAMP")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS resource_sections (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            title TEXT NOT NULL,
            order_index INTEGER NOT NULL,
            page_start INTEGER,
            page_end INTEGER,
            char_start INTEGER,
            char_end INTEGER,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sections_document_id ON resource_sections(document_id)"
    )

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
            section_id TEXT,
            checksum TEXT,
            token_estimate INTEGER,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY(section_id) REFERENCES resource_sections(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id)"
    )

    add_column(
        "document_chunks", "section_id TEXT REFERENCES resource_sections(id) ON DELETE CASCADE"
    )
    add_column("document_chunks", "checksum TEXT")
    add_column("document_chunks", "token_estimate INTEGER")

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

    # 6. Learner Activity
    conn.execute("""
        CREATE TABLE IF NOT EXISTS learner_activity (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data_json TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_learner_activity_user_id ON learner_activity(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_learner_activity_event_type ON learner_activity(event_type)"
    )
    
    # Milestone 5.1 extensions for learning events
    add_column(
        "learner_activity", "section_id TEXT REFERENCES resource_sections(id) ON DELETE CASCADE"
    )
    add_column(
        "learner_activity", "chunk_id TEXT REFERENCES document_chunks(id) ON DELETE CASCADE"
    )
    add_column("learner_activity", "occurred_at TIMESTAMP")
    add_column("learner_activity", "idempotency_key TEXT")

    # Add constraints
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_learner_activity_idempotency "
        "ON learner_activity(idempotency_key) WHERE idempotency_key IS NOT NULL"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_learner_activity_occurred_at "
        "ON learner_activity(occurred_at)"
    )
    
    # 7. Document Jobs
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_jobs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            error_message TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_document_jobs_user_id ON document_jobs(user_id)")
