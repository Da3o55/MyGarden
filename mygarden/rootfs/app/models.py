from database import get_connection

FIELDS = [
    "common_name", "scientific_name", "exposure", "soil_type",
    "plant_type", "hardiness", "soil_humidity", "foliage_type",
    "height_min", "height_max", "flowering_start", "flowering_end",
    "known_diseases", "pruning_start", "pruning_end", "pruning_advice",
    "fertilizing_start", "fertilizing_end", "fertilizing_quantity",
    "fertilizing_type", "image_url", "source_api_id", "notes",
    "garden_location", "date_planted"
]


def get_all_plants():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants ORDER BY common_name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_plant_by_id(plant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE id = ?", (plant_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_plant(data):
    conn = get_connection()
    cursor = conn.cursor()

    filtered = {k: v for k, v in data.items() if k in FIELDS}
    keys = ", ".join(filtered.keys())
    placeholders = ", ".join(["?"] * len(filtered))
    values = list(filtered.values())

    cursor.execute(
        f"INSERT INTO plants ({keys}) VALUES ({placeholders})",
        values
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_plant(plant_id, data):
    conn = get_connection()
    cursor = conn.cursor()

    filtered = {k: v for k, v in data.items() if k in FIELDS}
    set_clause = ", ".join([f"{k} = ?" for k in filtered.keys()])
    values = list(filtered.values()) + [plant_id]

    cursor.execute(
        f"UPDATE plants SET {set_clause} WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


def delete_plant(plant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
    conn.commit()
    conn.close()


def search_plants(query):
    conn = get_connection()
    cursor = conn.cursor()
    like_query = f"%{query}%"
    cursor.execute(
        """SELECT * FROM plants
           WHERE common_name LIKE ? OR scientific_name LIKE ?
           ORDER BY common_name""",
        (like_query, like_query)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]