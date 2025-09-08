import sqlite3

DB_NAME = "knowledge_base.db"

def create_database():
    """
    Creates a new SQLite database with the schema for our knowledge base.
    """
    try:
        # Connect to the database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print("--- Creating 'pests' table ---")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pests (
            PestID INTEGER PRIMARY KEY AUTOINCREMENT,
            PestCommonName TEXT NOT NULL UNIQUE,
            PestScientificName TEXT,
            PestInfo TEXT
        );
        """)

        print("--- Creating 'recommendations' table ---")
        # This table is based on the structure from the research document
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            RecommendationID INTEGER PRIMARY KEY AUTOINCREMENT,
            PestID INTEGER,
            RecommendationType TEXT CHECK(RecommendationType IN ('IPM', 'Chemical', 'Prevention')),
            RecommendationDetails TEXT NOT NULL,
            Source TEXT,
            LastVerifiedDate TEXT,
            FOREIGN KEY (PestID) REFERENCES pests (PestID)
        );
        """)

        # Commit the changes to the database
        conn.commit()
        print(f"✅ Database '{DB_NAME}' and tables created successfully.")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_database()