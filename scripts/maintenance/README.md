# Maintenance & Data Integrity Utilities

Procedures and maintenance scripts for managing the persistent SQLite and Chroma vector stores.

---

## Standard Maintenance Tasks

1. **SQLite Database Compaction**:
   Compacts and optimizes the primary database after large document removals:
   ```bash
   sqlite3 ./data/kogniq.db "VACUUM; PRAGMA optimize;"
   ```

2. **Orphaned Document Cleanup**:
   Re-links or cleans uploaded files that lack corresponding records in the `documents` table:
   ```python
   from backend.security.bootstrap import adopt_orphaned_documents
   adopt_orphaned_documents(demo_email="admin@kogniq.ai")
   ```

3. **Rebuild Chroma Vector Index**:
   Re-embeds and reindexes all stored chunks into a clean, unfragmented Chroma collection:
   Trigger via API: `POST /api/v1/documents/{document_id}/reindex`.
