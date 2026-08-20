import json, os
def load_options():
    for path in ("/data/options.json","/data/options.yaml"):
        if os.path.exists(path):
            try:
                if path.endswith("json"): return json.load(open(path))
            except (OSError, json.JSONDecodeError): pass
    return {"timezone":"Europe/Paris","trefle_token":""}
