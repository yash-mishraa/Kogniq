import os
import tempfile

_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_fd)

# Isolate all automated tests from the normal user workspace data
os.environ["SQLITE_DATABASE_PATH"] = _db_path
os.environ["PERSISTENCE_PROVIDER"] = "sqlite"
os.environ["CHROMA_DB_PATH"] = ":memory:"
