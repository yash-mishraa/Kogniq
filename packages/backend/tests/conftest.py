import os

# Force memory persistence provider for all tests to avoid writing to local SQLite database
os.environ["PERSISTENCE_PROVIDER"] = "memory"
