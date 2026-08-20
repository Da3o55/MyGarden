import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "/data/mygarden.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            common_name TEXT NOT NULL,
            scientific_name TEXT,
            exposure TEXT,
            soil_type TEXT,
            plant_type TEXT,
            hardiness TEXT,
            soil_humidity TEXT,
            foliage_type TEXT,
            height_min REAL,
            height_max REAL,
            flowering_start TEXT,
            flowering_end TEXT,
            known_diseases TEXT,
            pruning_start TEXT,
            pruning_end TEXT,
            pruning_advice TEXT,
            fertilizing_start TEXT,
            fertilizing_end TEXT,
            fertilizing_quantity TEXT,
            fertilizing_type TEXT,
            image_url TEXT,
            source_api_id TEXT,
            notes TEXT,
            garden_location TEXT,
            date_planted TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def seed_if_empty():
    """Ajoute des plantes de démo si la base est vide"""
    from seed_data import SEED_PLANTS

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM plants")
    count = cursor.fetchone()["count"]

    if count == 0:
        for plant in SEED_PLANTS:
            keys = ", ".join(plant.keys())
            placeholders = ", ".join(["?"] * len(plant))
            values = list(plant.values())
            cursor.execute(
                f"INSERT INTO plants ({keys}) VALUES ({placeholders})",
                values
            )
        conn.commit()

    conn.close()