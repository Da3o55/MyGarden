from flask import Flask, jsonify, request, send_from_directory
from datetime import date
import os
import requests

from database import init_db, seed_if_empty
import models

app = Flask(__name__, static_folder="static", static_url_path="")

PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY", "")
PERENUAL_BASE_URL = "https://perenual.com/api"


# ---------- Init ----------
init_db()
seed_if_empty()


# ---------- Utils calendrier ----------
def is_date_in_range(today, start_mmdd, end_mmdd):
    if not start_mmdd or not end_mmdd:
        return False
    try:
        current = (today.month, today.day)
        start = tuple(int(x) for x in start_mmdd.split("-"))
        end = tuple(int(x) for x in end_mmdd.split("-"))
    except (ValueError, AttributeError):
        return False

    if start <= end:
        return start <= current <= end
    else:
        return current >= start or current <= end


# ---------- Routes Frontend ----------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ---------- API Plants CRUD ----------
@app.route("/api/plants", methods=["GET"])
def api_get_plants():
    search = request.args.get("search")
    if search:
        plants = models.search_plants(search)
    else:
        plants = models.get_all_plants()
    return jsonify(plants)


@app.route("/api/plants/<int:plant_id>", methods=["GET"])
def api_get_plant(plant_id):
    plant = models.get_plant_by_id(plant_id)
    if not plant:
        return jsonify({"error": "Plante non trouvée"}), 404
    return jsonify(plant)


@app.route("/api/plants", methods=["POST"])
def api_create_plant():
    data = request.get_json()
    if not data or not data.get("common_name"):
        return jsonify({"error": "Le nom commun est requis"}), 400
    new_id = models.create_plant(data)
    return jsonify({"id": new_id}), 201


@app.route("/api/plants/<int:plant_id>", methods=["PUT"])
def api_update_plant(plant_id):
    data = request.get_json()
    models.update_plant(plant_id, data)
    return jsonify({"success": True})


@app.route("/api/plants/<int:plant_id>", methods=["DELETE"])
def api_delete_plant(plant_id):
    models.delete_plant(plant_id)
    return jsonify({"success": True})


# ---------- API Calendrier ----------
@app.route("/api/calendar/today", methods=["GET"])
def api_calendar_today():
    plants = models.get_all_plants()
    today = date.today()

    result = {"flowering": [], "pruning": [], "fertilizing": []}

    for plant in plants:
        base = {
            "id": plant["id"],
            "common_name": plant["common_name"],
            "scientific_name": plant["scientific_name"],
            "image_url": plant["image_url"]
        }

        if is_date_in_range(today, plant["flowering_start"], plant["flowering_end"]):
            result["flowering"].append(base)

        if is_date_in_range(today, plant["pruning_start"], plant["pruning_end"]):
            result["pruning"].append({**base, "advice": plant["pruning_advice"]})

        if is_date_in_range(today, plant["fertilizing_start"], plant["fertilizing_end"]):
            result["fertilizing"].append({
                **base,
                "quantity": plant["fertilizing_quantity"],
                "type": plant["fertilizing_type"]
            })

    return jsonify(result)


# ---------- API Recherche externe (Perenual) ----------
@app.route("/api/external/search", methods=["GET"])
def api_external_search():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Paramètre q requis"}), 400

    if not PERENUAL_API_KEY:
        return jsonify({"error": "Clé API Perenual non configurée"}), 400

    try:
        resp = requests.get(
            f"{PERENUAL_BASE_URL}/species-list",
            params={"key": PERENUAL_API_KEY, "q": query},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

        results = [
            {
                "id": item.get("id"),
                "common_name": item.get("common_name"),
                "scientific_name": ", ".join(item.get("scientific_name", []) or []),
                "image_url": (item.get("default_image") or {}).get("thumbnail")
            }
            for item in data
        ]
        return jsonify(results)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/external/plant/<int:external_id>", methods=["GET"])
def api_external_plant_details(external_id):
    if not PERENUAL_API_KEY:
        return jsonify({"error": "Clé API Perenual non configurée"}), 400

    try:
        resp = requests.get(
            f"{PERENUAL_BASE_URL}/species/details/{external_id}",
            params={"key": PERENUAL_API_KEY},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        watering_map = {"Frequent": "Humide", "Average": "Frais", "Minimum": "Sec"}
        sunlight = data.get("sunlight") or []

        mapped = {
            "common_name": data.get("common_name", ""),
            "scientific_name": ", ".join(data.get("scientific_name", []) or []),
            "exposure": ", ".join(sunlight) if sunlight else "",
            "soil_humidity": watering_map.get(data.get("watering"), ""),
            "foliage_type": "Persistant" if data.get("cycle") == "Perennial" else "Caduc",
            "plant_type": data.get("type", ""),
            "image_url": (data.get("default_image") or {}).get("original_url", ""),
            "source_api_id": str(data.get("id", "")),
            "known_diseases": "",
            "pruning_advice": "",
        }
        return jsonify(mapped)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099, debug=False)