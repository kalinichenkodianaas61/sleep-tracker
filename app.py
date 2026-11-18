from datetime import datetime
from flask import Flask, request, jsonify
import storage, logic
from models import SleepRecord, DEFAULT_FACTOR
from flask_cors import CORS
import os
from dotenv import load_dotenv
import hmac
from flask import abort

load_dotenv()  # Load variables from .env 

app = Flask(__name__)
# secret comes from environment, not from code 
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")

def require_admin():
    # Tunnel traffic carries Cloudflare headers, so admin works only locally
    if "Cf-Connecting-Ip" in request.headers:
        abort(403)
    token = request.headers.get("X-Admin-Token", "")
    # refuse if token is not set or does not match (відмова, якщо токен не заданий або не збігається)
    if not ADMIN_TOKEN or not hmac.compare_digest(token.encode(), ADMIN_TOKEN.encode()):
        abort(403)

CORS(app, origins=["https://kalinichenko2.pp.ua", "http://localhost:8080"])
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
    return jsonify([r.to_dict() for r in records])

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
        # the class checks quality and factor itself 
        record = SleepRecord(data["date"], data["sleep"], data["wake"],
                             data["quality"], data.get("factor", DEFAULT_FACTOR))
    except (ValueError, TypeError):
        return jsonify({"error": "date DD-MM-YY, time HH:MM, quality 1-100, "
                                 "factor up to 50 characters"}), 400
    new_id = storage.add(record)
    return jsonify({"id": new_id}), 201

@app.delete("/admin/records/<int:item_id>")
def delete_record(item_id):
    require_admin()
    if storage.delete(item_id):
        return jsonify({"deleted": item_id})
    return jsonify({"error": "не знайдено"}), 404

@app.get("/admin/export")
def export_records():
    require_admin()
    return jsonify([r.to_dict() for r in storage.load()])


@app.get("/admin/log")
def admin_log():
    require_admin()
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    limit = max(1, min(limit, 500))  # keep it reasonable 
    return jsonify(storage.load_log(limit))

@app.get("/report/factors")
def report_factors():
    # report built with JOIN of records and factors
    return jsonify(storage.factor_report())


@app.get("/report")
def report():
    return jsonify({"average_sleep": logic.average_sleep(storage.load())})

if __name__ == "__main__":
    app.run()  # no debug mode 