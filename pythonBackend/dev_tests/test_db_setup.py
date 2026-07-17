import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()
# ============================
# DATABASE CONNECTION
# ============================
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

# Table 1: songs
cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255),
        artist VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# Table 2: fingerprints
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fingerprints (
        id SERIAL PRIMARY KEY,
        hash VARCHAR(40),
        song_id INTEGER REFERENCES songs(id),
        anchor_time INTEGER
    )
""")

# Fast searching ke liye index banao hash column pe
cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints(hash)")

conn.commit()
print("Tables created successfully!")

cursor.close()
conn.close()