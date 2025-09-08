import sqlite3
import pandas as pd
import datetime

DB_NAME = "src/api/knowledge_base.db"
CSV_PATH = "cibrc_data.csv"
SOURCE_NAME = "CIB&RC"
RECOMMENDATION_TYPE = "Chemical"
LAST_VERIFIED = datetime.date.today().isoformat()

def populate_db_from_csv():
    """
    Reads the scraped CIB&RC data from the CSV and inserts it into the database.
    """
    try:
        # Load the scraped data
        df = pd.read_csv(CSV_PATH)

        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print(f"--- Populating database from '{CSV_PATH}' ---")

        inserted_count = 0
        # Use a set to keep track of pests we've already added
        known_pests = set(row[0] for row in cursor.execute("SELECT PestCommonName FROM pests"))

        for _, row in df.iterrows():
            # Normalize the pest name to be consistent
            pest_name = str(row['pest_name']).strip().lower().replace(' ', '_')
            chemical = str(row['chemical_name']).strip()
            dosage = str(row['dosage']).strip()

            # Full recommendation detail
            recommendation_detail = f"{chemical} (Dosage: {dosage})"

            # 1. Insert the pest into the 'pests' table if it's new
            if pest_name not in known_pests:
                cursor.execute(
                    "INSERT INTO pests (PestCommonName) VALUES (?)",
                    (pest_name,)
                )
                known_pests.add(pest_name)

            # 2. Get the PestID for the current pest
            cursor.execute("SELECT PestID FROM pests WHERE PestCommonName = ?", (pest_name,))
            result = cursor.fetchone()
            if result is None:
                continue # Should not happen, but as a safeguard
            pest_id = result[0]

            # 3. Insert the chemical recommendation
            cursor.execute("""
                INSERT INTO recommendations 
                (PestID, RecommendationType, RecommendationDetails, Source, LastVerifiedDate)
                VALUES (?, ?, ?, ?, ?)
            """, (pest_id, RECOMMENDATION_TYPE, recommendation_detail, SOURCE_NAME, LAST_VERIFIED))
            inserted_count += 1

        conn.commit()
        print(f"✅ Database population complete. Inserted {inserted_count} new chemical recommendations.")

    except (sqlite3.Error, pd.errors.EmptyDataError, FileNotFoundError) as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    populate_db_from_csv()