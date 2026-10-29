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
        CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_states_user_resource
        ON knowledge_states(user_id, resource_id)
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
    add_column("learner_activity", "chunk_id TEXT REFERENCES document_chunks(id) ON DELETE CASCADE")
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

    # 7.5 Document Semantics
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_semantics (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            semantic_version TEXT NOT NULL,
            status TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 0,
            semantics_json TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_document_semantics_doc_id "
        "ON document_semantics(document_id)"
    )
    # Ensure at most one active version per document
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_document_semantics_active "
        "ON document_semantics(document_id) WHERE is_active = 1"
    )

    # 8. Agent Chat Memory
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            document_id TEXT,
            title TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tool_events TEXT,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)"
    )

    # 9. Notebook Entries (M7)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notebook_entries (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            document_id TEXT NOT NULL,
            title TEXT NOT NULL,
            thoughts_json TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            idempotency_key TEXT,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_notebook_entries_user_id ON notebook_entries(user_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_notebook_entries_document_id "
        "ON notebook_entries(document_id)"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_notebook_entries_idempotency "
        "ON notebook_entries(idempotency_key) WHERE idempotency_key IS NOT NULL"
    )

    # 10. Persistent authentication (RAG product)
    # The historical application kept users and sessions in memory, which meant
    # every process restart invalidated sessions and orphaned owned documents.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_credentials (
            user_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS auth_sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id)"
    )

    # 11. Index state: the authoritative record of whether a document's chunks
    # were successfully embedded and written to the vector index. A document is
    # never reported as ready unless this row says "Ready".
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS document_index_state (
            document_id TEXT PRIMARY KEY,
            user_id TEXT,
            status TEXT NOT NULL,
            error_message TEXT,
            chunk_count INTEGER NOT NULL DEFAULT 0,
            embedding_model TEXT,
            embedding_dimensions INTEGER,
            chunker_config TEXT,
            indexed_at TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )
    # Early development builds accidentally gave this table a foreign key to
    # ``documents``. That makes it impossible to record "Processing" before the
    # pipeline has created the document row. Rebuild the table in place if an
    # old definition is present.
    fk_rows = conn.execute("PRAGMA foreign_key_list(document_index_state)").fetchall()
    if fk_rows:
        conn.execute("ALTER TABLE document_index_state RENAME TO document_index_state_legacy")
        conn.execute(
            """
            CREATE TABLE document_index_state (
                document_id TEXT PRIMARY KEY,
                user_id TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                embedding_model TEXT,
                embedding_dimensions INTEGER,
                chunker_config TEXT,
                indexed_at TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO document_index_state (
                document_id, user_id, status, error_message, chunk_count,
                embedding_model, embedding_dimensions, chunker_config, indexed_at, updated_at
            )
            SELECT document_id, user_id, status, error_message, chunk_count,
                   embedding_model, embedding_dimensions, chunker_config, indexed_at, updated_at
            FROM document_index_state_legacy
            """
        )
        conn.execute("DROP TABLE document_index_state_legacy")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_document_index_state_user_id "
        "ON document_index_state(user_id)"
    )

    # 12. Query telemetry. Deliberately stores only the user's query text and
    # operational counters; prompts and retrieved document text are never logged.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS query_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            query_text TEXT NOT NULL,
            document_ids_json TEXT,
            strategy TEXT,
            status TEXT NOT NULL,
            error_category TEXT,
            retrieval_ms REAL,
            generation_ms REAL,
            total_ms REAL,
            candidate_count INTEGER,
            selected_count INTEGER,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            model TEXT,
            provider TEXT,
            citation_count INTEGER,
            citations_valid INTEGER,
            cache_status TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_query_logs_user_created "
        "ON query_logs(user_id, created_at DESC)"
    )

    # 13. Reproducible evaluation runs
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluation_runs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            dataset_id TEXT NOT NULL,
            document_id TEXT,
            status TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            details_json TEXT NOT NULL,
            duration_ms REAL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_evaluation_runs_user_created "
        "ON evaluation_runs(user_id, created_at DESC)"
    )

    # 14. Index configuration metadata (embedding model identity, dimensions,
    # collection name, chunker version). Used to refuse incompatible mixes.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS index_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    # 15. Lexical index for genuine hybrid retrieval (BM25 via FTS5).
    # Triggers keep the lexical index in sync with SQLite-authoritative chunks.
    try:
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts USING fts5(
                chunk_id UNINDEXED,
                document_id UNINDEXED,
                text,
                tokenize='porter unicode61'
            )
            """
        )
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_chunks_fts_insert
            AFTER INSERT ON document_chunks BEGIN
                INSERT INTO document_chunks_fts(rowid, chunk_id, document_id, text)
                VALUES (new.rowid, new.id, new.document_id, new.text);
            END
            """
        )
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_chunks_fts_delete
            AFTER DELETE ON document_chunks BEGIN
                DELETE FROM document_chunks_fts WHERE rowid = old.rowid;
            END
            """
        )
        conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS trg_chunks_fts_update
            AFTER UPDATE OF text ON document_chunks BEGIN
                DELETE FROM document_chunks_fts WHERE rowid = old.rowid;
                INSERT INTO document_chunks_fts(rowid, chunk_id, document_id, text)
                VALUES (new.rowid, new.id, new.document_id, new.text);
            END
            """
        )
        conn.execute(
            """
            INSERT INTO document_chunks_fts(rowid, chunk_id, document_id, text)
            SELECT c.rowid, c.id, c.document_id, c.text
            FROM document_chunks c
            WHERE NOT EXISTS (
                SELECT 1 FROM document_chunks_fts f WHERE f.rowid = c.rowid
            )
            """
        )
    except sqlite3.OperationalError:
        # FTS5 is optional. Hybrid retrieval degrades explicitly to vector-only
        # when the SQLite build lacks FTS5; it never silently fakes lexical hits.
        pass
