from flask import Flask, jsonify, send_from_directory, request
from models import db, Reading
from datetime import datetime, timedelta, timezone
from collections import defaultdict

app = Flask(__name__, static_folder='../frontend', static_url_path='/')

# FIXED DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

EMISSIONS_FACTOR_KGCO2_PER_KWH = 0.5


tables_created = False

@app.before_request
def create_tables_once():
    global tables_created
    if not tables_created:
        db.create_all()
        tables_created = True



@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# ------------------------------
# POST /api/readings
# ------------------------------
@app.route('/api/readings', methods=['POST'])
def post_reading():
    data = request.get_json()

    if not data:
        return jsonify({"error": "missing JSON"}), 400

    device = data.get("device", "unknown")

    try:
        watts = float(data.get("watts"))
    except:
        return jsonify({"error": "invalid watts value"}), 400

    ts = data.get("timestamp")

    if ts:
        try:
            timestamp = datetime.fromisoformat(ts)
        except:
            timestamp = datetime.now(timezone.utc)
    else:
        timestamp = datetime.now(timezone.utc)

    r = Reading(device=device, watts=watts, timestamp=timestamp)

    db.session.add(r)
    db.session.commit()

    return jsonify(r.to_dict()), 201


# ------------------------------
# GET /api/readings
# ------------------------------
@app.route('/api/readings', methods=['GET'])
def get_readings():
    start = request.args.get("start")
    end = request.args.get("end")

    q = Reading.query

    if start:
        try:
            start_dt = datetime.fromisoformat(start)
            q = q.filter(Reading.timestamp >= start_dt)
        except:
            pass

    if end:
        try:
            end_dt = datetime.fromisoformat(end)
            q = q.filter(Reading.timestamp <= end_dt)
        except:
            pass

    readings = q.order_by(Reading.timestamp.asc()).all()
    return jsonify([r.to_dict() for r in readings])


# ------------------------------
# GET /api/aggregates/daily
# ------------------------------
@app.route('/api/aggregates/daily', methods=['GET'])
def daily_aggregates():
    days = int(request.args.get('days', 7))
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    readings = Reading.query.filter(
        Reading.timestamp >= start
    ).order_by(Reading.timestamp.asc()).all()

    energy_by_day_wh = defaultdict(float)

    if len(readings) >= 2:
        for i in range(1, len(readings)):
            prev = readings[i-1]
            curr = readings[i]

            sec = (curr.timestamp - prev.timestamp).total_seconds()
            avg_w = (prev.watts + curr.watts) / 2.0
            wh = avg_w * sec / 3600.0

            day_key = prev.timestamp.date().isoformat()
            energy_by_day_wh[day_key] += wh

    days_list = []
    for d in range(days - 1, -1, -1):
        day = (end - timedelta(days=d)).date().isoformat()
        wh = energy_by_day_wh.get(day, 0)
        days_list.append({
            "date": day,
            "wh": round(wh, 3),
            "kwh": round(wh / 1000.0, 4),
        })

    return jsonify(days_list)


# ------------------------------
# GET /api/summary
# ------------------------------
@app.route('/api/summary', methods=['GET'])
def summary():
    subq = db.session.query(
        Reading.device,
        db.func.max(Reading.timestamp).label("latest")
    ).group_by(Reading.device).subquery()

    last = db.session.query(Reading).join(
        subq,
        (Reading.device == subq.c.device) &
        (Reading.timestamp == subq.c.latest)
    ).all()

    total = sum(r.watts for r in last)

    return jsonify({
        "total_watts": total,
        "devices": [r.to_dict() for r in last]
    })


# ------------------------------
# GET /api/co2
# ------------------------------
@app.route('/api/co2', methods=['GET'])
def co2():
    days = int(request.args.get("days", 7))
    daily = daily_aggregates().get_json()

    total_kwh = sum(d["kwh"] for d in daily)
    total_co2 = total_kwh * EMISSIONS_FACTOR_KGCO2_PER_KWH

    return jsonify({
        "kwh": round(total_kwh, 3),
        "kgCO2": round(total_co2, 3),
        "factor_kgCO2_per_kWh": EMISSIONS_FACTOR_KGCO2_PER_KWH
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
