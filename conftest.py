import os

# Isolate all automated tests from the normal user workspace data
os.environ["SQLITE_DATABASE_PATH"] = ":memory:"
os.environ["PERSISTENCE_PROVIDER"] = "sqlite"
os.environ["CHROMA_DB_PATH"] = ":memory:"
