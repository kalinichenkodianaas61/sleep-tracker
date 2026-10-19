from datetime import datetime
from flask import Flask, request, jsonify
import storage, logic

app = Flask(__name__)
storage.init()

@app.get("/records")
def list_records():
    records = storage.load()
    # optional filter ?min_quality=3&max_quality=5 
    lo = request.args.get("min_quality")
    hi = request.args.get("max_quality")
    if lo is not None and hi is not None:
        try:
            records = logic.find_by_quality(records, int(lo), int(hi))
        except ValueError:
            return jsonify({"error": "min_quality and max_quality must be an integer"}), 400
    return jsonify(records)

@app.post("/records")
def add_record():
    data = request.get_json(silent=True)
    if data is None:  # no JSON body 
        return jsonify({"error": "expected JSON"}), 400
    for f in ("date", "sleep", "wake", "quality"):
        if f not in data:
            return jsonify({"error": f"no field {f}"}), 400
    try:
        # validate formats, otherwise report would crash later 
        datetime.strptime(data["date"], "%d-%m-%y")
        datetime.strptime(data["sleep"], "%H:%M")
        datetime.strptime(data["wake"], "%H:%M")
        quality = int(data["quality"])
    except (ValueError, TypeError):
        return jsonify({"error": "date DD-MM-JJ, time HH:MM, quality integer"}), 400
    new_id = storage.add(data["date"], data["sleep"], data["wake"], quality)
    return jsonify({"id": new_id}), 201

@app.delete("/records/<int:item_id>")
def delete_record(item_id):
    if storage.delete(item_id):
        return jsonify({"deleted": item_id})
    return jsonify({"error": "not found"}), 404

@app.get("/report")
def report():
    return jsonify({"average_sleep": logic.average_sleep(storage.load())})

if __name__ == "__main__":
    app.run(debug=True)