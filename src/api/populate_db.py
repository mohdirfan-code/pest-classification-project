import sqlite3
import datetime

DB_NAME = "knowledge_base.db"
LAST_VERIFIED = datetime.date.today().isoformat()

# This data is curated from the research documents you provided.
PEST_DATA = {
    "bollworm": {
        "scientific_name": "Helicoverpa armigera",
        "info": "The cotton bollworm is a highly destructive pest that attacks a wide range of crops including cotton, tomato, corn, and legumes. The larvae bore into bolls, buds, and fruits, causing significant yield losses.",
        "recommendations": [
            ("IPM", "Introduce natural predators like Trichogramma wasps and Chrysoperla carnea.", "ICAR"),
            ("IPM", "Use pheromone traps to monitor adult moth activity and disrupt mating.", "ICAR"),
            ("Chemical", "Emamectin Benzoate 5% SG (Dosage: 100g per acre)", "CIB&RC / SAU Guidelines"),
            ("Chemical", "Chlorantraniliprole 18.5% SC (Dosage: 60ml per acre)", "CIB&RC / SAU Guidelines"),
            ("Prevention", "Practice crop rotation with non-host plants like cereals or grasses.", "ICAR"),
            ("Prevention", "Ensure timely sowing of crops to avoid peak pest pressure periods.", "ICAR"),
        ]
    },
    "brown plant hopper": {
        "scientific_name": "Nilaparvata lugens",
        "info": "A major pest of rice, the Brown Plant Hopper (BPH) sucks sap from the base of the plants, causing 'hopperburn' - the yellowing and drying of the crop. They can cause complete crop failure in cases of severe infestation.",
        "recommendations": [
            ("IPM", "Practice alternate wetting and drying (AWD) of the field to create an unfavorable environment for the hopper.", "TNAU"),
            ("IPM", "Release natural predators like spiders, mirid bugs, and damselflies.", "ICAR-NRRI"),
            ("Chemical", "Buprofezin 25% SC (Dosage: 325 ml/acre)", "CIB&RC"),
            ("Chemical", "Imidacloprid 17.8% SL (Dosage: 50-60 ml/acre)", "CIB&RC"),
            ("Prevention", "Use BPH-resistant rice varieties like 'PY 3' or 'CO 42' if available in your region.", "TNAU"),
            ("Prevention", "Provide 30cm rogue spacing at every 2.5m to improve air circulation and reduce pest buildup.", "TNAU"),
        ]
    },
    "yellow rice borer": {
        "scientific_name": "Scirpophaga incertulas",
        "info": "Commonly known as the rice yellow stem borer, the larvae bore into the rice stem. Early-stage infestation causes 'deadhearts' (dead central shoots), while late-stage infestation causes 'white ears' (empty panicles).",
        "recommendations": [
            ("IPM", "Release the egg parasitoid Trichogramma japonicum at weekly intervals.", "ICAR"),
            ("IPM", "Use pheromone traps at a rate of 8 per acre for monitoring and mass trapping.", "ICAR"),
            ("Chemical", "Chlorantraniliprole 0.4% GR (Dosage: 4 kg/acre)", "CIB&RC"),
            ("Chemical", "Cartap Hydrochloride 4% G (Dosage: 10 kg/acre)", "CIB&RC"),
            ("Prevention", "Clip the tips of seedlings before transplanting to remove egg masses.", "ICAR-NRRI"),
            ("Prevention", "Harvest the crop close to the ground level to destroy the stubble where larvae may be hiding.", "ICAR-NRRI"),
        ]
    }
}

def populate_database():
    """
    Connects to the database and inserts the curated pest data.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        print("--- Populating database with authoritative data ---")

        for pest_common_name, data in PEST_DATA.items():
            print(f"  -> Processing: {pest_common_name}")

            # 1. Insert the pest into the 'pests' table
            try:
                cursor.execute("""
                INSERT INTO pests (PestCommonName, PestScientificName, PestInfo)
                VALUES (?, ?, ?);
                """, (pest_common_name, data["scientific_name"], data["info"]))
                
                pest_id = cursor.lastrowid
                print(f"     - Added '{pest_common_name}' to pests table with ID: {pest_id}")

                # 2. Insert all associated recommendations
                for rec_type, details, source in data["recommendations"]:
                    cursor.execute("""
                    INSERT INTO recommendations (PestID, RecommendationType, RecommendationDetails, Source, LastVerifiedDate)
                    VALUES (?, ?, ?, ?, ?);
                    """, (pest_id, rec_type, details, source, LAST_VERIFIED))
                
                print(f"     - Added {len(data['recommendations'])} recommendations.")

            except sqlite3.IntegrityError:
                print(f"     - Pest '{pest_common_name}' already exists. Skipping insertion.")

        conn.commit()
        print("\n✅ Database population complete.")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    populate_database()