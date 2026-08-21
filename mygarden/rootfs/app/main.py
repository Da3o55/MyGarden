import os
import sqlite3
import requests
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
import paho.mqtt.client as mqtt
import threading
import time
import json

app = Flask(__name__, static_folder="static", static_url_path="")

DB_PATH = os.environ.get("DB_PATH", "/data/mygarden.db")
PERENUAL_API_KEY = os.environ.get("PERENUAL_API_KEY", "")
PERENUAL_BASE_URL = "https://perenual.com/api"

MONTHS_FR = [
    "", "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
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
            height TEXT,
            bloom_start_month INTEGER,
            bloom_end_month INTEGER,
            known_diseases TEXT,
            pruning_start_month INTEGER,
            pruning_end_month INTEGER,
            pruning_advice TEXT,
            fertilize_start_month INTEGER,
            fertilize_end_month INTEGER,
            fertilize_quantity TEXT,
            fertilize_type TEXT,
            image_url TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) as c FROM plants").fetchone()["c"]
    if count == 0:
        seed_data(conn)
    conn.close()


def seed_data(conn):
    plants = [
        ("Rosier", "Rosa", "Plein soleil", "Riche, drainé", "Arbuste", "Zone 5-9",
         "Modérée", "Caduc", "1-2 m", 5, 9, "Oïdium, taches noires, puceron",
         2, 3, "Tailler en fin d'hiver, couper les tiges mortes à 45°, garder 3-5 branches vigoureuses",
         3, 8, "Toutes les 6 semaines", "Engrais riche en potasse", "", ""),
        ("Lavande", "Lavandula angustifolia", "Plein soleil", "Sableux, drainé", "Arbuste", "Zone 5-9",
         "Faible", "Persistant", "30-60 cm", 6, 8, "Pourriture racinaire si excès d'eau",
         3, 4, "Tailler après floraison, ne pas couper dans le bois vieux",
         4, 5, "Une fois par an", "Engrais pauvre en azote", "", ""),
        ("Pommier", "Malus domestica", "Plein soleil", "Riche, drainé", "Fruitier", "Zone 4-8",
         "Modérée", "Caduc", "3-8 m", 4, 5, "Tavelure, chancre, puceron lanigère",
         12, 2, "Taille de formation en hiver, retirer bois mort et gourmands",
         3, 6, "2 fois par saison", "Engrais NPK équilibré + compost", "", ""),
        ("Hortensia", "Hydrangea macrophylla", "Mi-ombre", "Riche, humide", "Arbuste", "Zone 6-9",
         "Modérée à élevée", "Caduc", "1-2 m", 6, 9, "Oïdium, chlorose",
         3, 3, "Couper les tiges fanées juste au-dessus du premier bourgeon",
         4, 7, "Toutes les 4 semaines", "Engrais spécial hortensia", "", ""),
        ("Tomate", "Solanum lycopersicum", "Plein soleil", "Riche, drainé", "Potager", "Annuelle",
         "Élevée", "N/A", "1-2 m", 6, 9, "Mildiou, oïdium",
         6, 8, "Supprimer les gourmands régulièrement, tailler les feuilles basses",
         5, 8, "Toutes les 2 semaines", "Engrais riche en potasse", "", ""),
    ]
    conn.executemany("""
        INSERT INTO plants (
            common_name, scientific_name, exposure, soil_type, plant_type,
            hardiness, soil_humidity, foliage_type, height,
            bloom_start_month, bloom_end_month, known_diseases,
            pruning_start_month, pruning_end_month, pruning_advice,
            fertilize_start_month, fertilize_end_month, fertilize_quantity,
            fertilize_type, image_url, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, plants)
    conn.commit()


def month_in_range(current_month, start, end):
    if start is None or end is None:
        return False
    if start <= end:
        return start <= current_month <= end
    else:
        return current_month >= start or current_month <= end

# ---------------- Routes statiques ----------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ---------------- API CRUD ----------------

@app.route("/api/plants", methods=["GET"])
def list_plants():
    conn = get_db()
    plants = conn.execute("SELECT * FROM plants ORDER BY common_name").fetchall()
    conn.close()
    return jsonify([dict(p) for p in plants])


@app.route("/api/plants/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    conn = get_db()
    plant = conn.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    conn.close()
    if plant is None:
        return jsonify({"error": "Plante non trouvée"}), 404
    return jsonify(dict(plant))


@app.route("/api/plants", methods=["POST"])
def create_plant():
    data = request.json
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO plants (
            common_name, scientific_name, exposure, soil_type, plant_type,
            hardiness, soil_humidity, foliage_type, height,
            bloom_start_month, bloom_end_month, known_diseases,
            pruning_start_month, pruning_end_month, pruning_advice,
            fertilize_start_month, fertilize_end_month, fertilize_quantity,
            fertilize_type, image_url, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("common_name"), data.get("scientific_name"), data.get("exposure"),
        data.get("soil_type"), data.get("plant_type"), data.get("hardiness"),
        data.get("soil_humidity"), data.get("foliage_type"), data.get("height"),
        data.get("bloom_start_month"), data.get("bloom_end_month"), data.get("known_diseases"),
        data.get("pruning_start_month"), data.get("pruning_end_month"), data.get("pruning_advice"),
        data.get("fertilize_start_month"), data.get("fertilize_end_month"),
        data.get("fertilize_quantity"), data.get("fertilize_type"),
        data.get("image_url"), data.get("notes")
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "message": "Plante ajoutée"}), 201


@app.route("/api/plants/<int:plant_id>", methods=["PUT"])
def update_plant(plant_id):
    data = request.json
    conn = get_db()
    conn.execute("""
        UPDATE plants SET
            common_name=?, scientific_name=?, exposure=?, soil_type=?, plant_type=?,
            hardiness=?, soil_humidity=?, foliage_type=?, height=?,
            bloom_start_month=?, bloom_end_month=?, known_diseases=?,
            pruning_start_month=?, pruning_end_month=?, pruning_advice=?,
            fertilize_start_month=?, fertilize_end_month=?, fertilize_quantity=?,
            fertilize_type=?, image_url=?, notes=?
        WHERE id=?
    """, (
        data.get("common_name"), data.get("scientific_name"), data.get("exposure"),
        data.get("soil_type"), data.get("plant_type"), data.get("hardiness"),
        data.get("soil_humidity"), data.get("foliage_type"), data.get("height"),
        data.get("bloom_start_month"), data.get("bloom_end_month"), data.get("known_diseases"),
        data.get("pruning_start_month"), data.get("pruning_end_month"), data.get("pruning_advice"),
        data.get("fertilize_start_month"), data.get("fertilize_end_month"),
        data.get("fertilize_quantity"), data.get("fertilize_type"),
        data.get("image_url"), data.get("notes"), plant_id
    ))
    conn.commit()
    conn.close()
    print("mise à jour de la plan")
    return jsonify({"message": "Plante mise à jour"})


@app.route("/api/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    conn = get_db()
    conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Plante supprimée"})


# ---------------- Calendrier du jour ----------------

@app.route("/api/today", methods=["GET"])
def today_events():
    now = datetime.now()
    current_month = now.month

    conn = get_db()
    plants = conn.execute("SELECT * FROM plants").fetchall()
    conn.close()

    result = {
        "date": now.strftime("%d/%m/%Y"),
        "month_name": MONTHS_FR[current_month],
        "blooming": [],
        "pruning": [],
        "fertilizing": []
    }

    for p in plants:
        p = dict(p)
        if month_in_range(current_month, p["bloom_start_month"], p["bloom_end_month"]):
            result["blooming"].append(p)
        if month_in_range(current_month, p["pruning_start_month"], p["pruning_end_month"]):
            result["pruning"].append(p)
        if month_in_range(current_month, p["fertilize_start_month"], p["fertilize_end_month"]):
            result["fertilizing"].append(p)

    return jsonify(result)


# ---------------- API externe Perenual ----------------

@app.route("/api/external-search", methods=["GET"])
def external_search():
    query = request.args.get("q", "")
    if not PERENUAL_API_KEY:
        return jsonify({"error": "Clé API Perenual non configurée"}), 400
    if not query:
        return jsonify({"results": []})

    try:
        resp = requests.get(
            f"{PERENUAL_BASE_URL}/species-list",
            params={"key": PERENUAL_API_KEY, "q": query},
            timeout=10
        )
        data = resp.json()
        results = []
        for item in data.get("data", []):
            results.append({
                "external_id": item.get("id"),
                "common_name": item.get("common_name"),
                "scientific_name": ", ".join(item.get("scientific_name", []) or []),
                "image_url": (item.get("default_image") or {}).get("regular_url", "")
            })
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/external-detail/<int:external_id>", methods=["GET"])
def external_detail(external_id):
    if not PERENUAL_API_KEY:
        return jsonify({"error": "Clé API Perenual non configurée"}), 400

    try:
        resp = requests.get(
            f"{PERENUAL_BASE_URL}/species/details/{external_id}",
            params={"key": PERENUAL_API_KEY},
            timeout=10
        )
        item = resp.json()

        sunlight = item.get("sunlight") or []
        watering = item.get("watering") or ""
        cycle = item.get("cycle") or ""
        hardiness = item.get("hardiness") or {}
        hardiness_str = ""
        if hardiness:
            hardiness_str = f"Zone {hardiness.get('min', '')}-{hardiness.get('max', '')}"

        mapped = {
            "common_name": item.get("common_name", ""),
            "scientific_name": ", ".join(item.get("scientific_name", []) or []),
            "exposure": ", ".join(sunlight) if sunlight else "",
            "plant_type": cycle.capitalize() if cycle else "Fleur",
            "hardiness": hardiness_str,
            "soil_humidity": watering,
            "foliage_type": "Persistant" if item.get("evergreen") else "Caduc",
            "image_url": (item.get("default_image") or {}).get("regular_url", ""),
        }
        return jsonify(mapped)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- MQTT ----------
MQTT_HOST = os.environ.get("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASS = os.environ.get("MQTT_PASS", "")

def publish_today_to_mqtt():
    print(f">>> MQTT_HOST={os.environ.get('MQTT_HOST')}")
    if not os.environ.get("MQTT_HOST"):
        print(">>> MQTT non configuré, publication ignorée.")
        return
    # ... reste du code

    now = datetime.now()
    current_month = now.month

    conn = get_db()
    plants = conn.execute("SELECT * FROM plants").fetchall()
    conn.close()

    blooming, pruning, fertilizing = [], [], []
    for p in plants:
        p = dict(p)
        print(p["common_name"])
        if month_in_range(current_month, p["bloom_start_month"], p["bloom_end_month"]):
            blooming.append(p["common_name"])
            print("Blooming : "+p["common_name"])
        if month_in_range(current_month, p["pruning_start_month"], p["pruning_end_month"]):
            pruning.append(p["common_name"])
            print("Pruning : "+p["common_name"])
        if month_in_range(current_month, p["fertilize_start_month"], p["fertilize_end_month"]):
            fertilizing.append(p["common_name"])
            print("Fertilizig : "+p["common_name"])

    client = mqtt.Client()
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    discovery_configs = {
        "mygarden_blooming": ("Floraison en cours", "mdi:flower"),
        "mygarden_pruning": ("Taille à prévoir", "mdi:content-cut"),
        "mygarden_fertilizing": ("Engrais à prévoir", "mdi:sprout"),
    }

    for obj_id, (name, icon) in discovery_configs.items():

        config_topic = f"hadev/sensor/{obj_id}/config"
        config_payload = {
            "name": name,
            "state_topic": f"mygarden/{obj_id}/state",
            "json_attributes_topic": f"mygarden/{obj_id}/attributes",
            "icon": icon,
            "unique_id": obj_id
        }
        client.publish(config_topic, json.dumps(config_payload), retain=True)

    client.publish("mygarden/mygarden_blooming/state", str(len(blooming)), retain=True)
    client.publish("mygarden/mygarden_blooming/attributes",
                    json.dumps({"plants": blooming}), retain=True)

    client.publish("mygarden/mygarden_pruning/state", str(len(pruning)), retain=True)
    client.publish("mygarden/mygarden_pruning/attributes",
                    json.dumps({"plants": pruning}), retain=True)

    client.publish("mygarden/mygarden_fertilizing/state", str(len(fertilizing)), retain=True)
    client.publish("mygarden/mygarden_fertilizing/attributes",
                    json.dumps({"plants": fertilizing}), retain=True)
    print(f">>> disconnect moduto")
    client.disconnect()

def daily_scheduler():
    print(">>> ENTREE dans daily_scheduler", flush=True)
    schedule_hour = 9
    schedule_minute = 0
    last_run = None
    
    while True:
        try:
            now = datetime.now()
            
            if (now.hour == schedule_hour and 
                now.minute == schedule_minute and 
                last_run != now.date()):
                
                print("🌱 Démarrage du job daily")
                
                plants = get_plants_from_db()
                print(f"📦 {len(plants)} plantes trouvées")
                
                for plant in plants:
                    try:
                        plant_data = get_plant_from_perenual(plant['id'])
                        
                        if plant_data:
                            payload = {
                                "id": plant['id'],
                                "name": plant['name'],
                                "watering": plant_data.get("watering", "N/A"),
                                "sunlight": plant_data.get("sunlight", []),
                                "last_updated": datetime.now().isoformat()
                            }
                            
                            topic = f"homeassistant/mygarden/plant/{plant['id']}"
                            client.publish(topic, json.dumps(payload), qos=1, retain=True)
                            print(f"✅ {plant['name']} publié")
                            
                    except Exception as e:
                        print(f"❌ Erreur pour {plant['name']}: {e}")
                
                print("✅ Job daily terminé")
                last_run = now.date()
            
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ Erreur scheduler: {e}")
            time.sleep(30)

if __name__ == "__main__":
    print(">>> AVANT init_db", flush=True)
    init_db()
    print(">>> APRES init_db", flush=True)
    
    print("MyGarden execution ...", flush=True)
    
    print(">>> AVANT création thread", flush=True)
    scheduler_thread = threading.Thread(target=publish_today_to_mqtt, daemon=True)
    print(">>> APRES création thread", flush=True)
    
    scheduler_thread.start()
    print(">>> APRES start() du thread", flush=True)
    
    print(">>> AVANT app.run", flush=True)
    app.run(host="0.0.0.0", port=8099)
