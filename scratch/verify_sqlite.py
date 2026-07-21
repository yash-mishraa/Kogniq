import sqlite3

print("--- Step 4: Tables ---")
conn = sqlite3.connect("data/demo_kogniq.db")
print("Tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
print("Documents:", conn.execute("SELECT * FROM documents;").fetchall())

print("\n--- Step 5: WAL Mode ---")
print("Journal Mode:", conn.execute("PRAGMA journal_mode;").fetchone())

print("\n--- Step 6: Foreign Keys ---")
print("Foreign Keys:", conn.execute("PRAGMA foreign_keys;").fetchone())
