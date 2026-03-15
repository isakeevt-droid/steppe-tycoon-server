from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)

DB_PATH = "steppe_tycoon.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            state TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

@app.route("/")
def home():
    return "Steppe Tycoon API works"

@app.route("/get/<user_id>")
def get_user(user_id):
    db = get_db()
    row = db.execute("SELECT state FROM players WHERE id = ?", (str(user_id),)).fetchone()
    db.close()

    if row:
        state = json.loads(row["state"])
        return jsonify({
            "id": str(user_id),
            "money": state.get("balance", 0),
            "level": max(1, int(state.get("totalEarned", 0)) // 5000 + 1)
        })

    return jsonify({
        "id": str(user_id),
        "money": 0,
        "level": 1
    })

@app.route("/get_state/<user_id>")
def get_state(user_id):
    db = get_db()
    row = db.execute("SELECT state FROM players WHERE id = ?", (str(user_id),)).fetchone()
    db.close()

    if row:
        return jsonify({
            "id": str(user_id),
            "state": json.loads(row["state"])
        })

    return jsonify({
        "id": str(user_id),
        "state": None
    })

@app.route("/save", methods=["POST"])
def save_simple():
    data = request.get_json(force=True)
    user_id = str(data.get("id"))
    money = int(data.get("money", 0))
    level = int(data.get("level", 1))

    state = {
        "name": "Игрок",
        "balance": money,
        "totalEarned": max(money, (level - 1) * 5000)
    }

    db = get_db()
    db.execute("""
        INSERT INTO players (id, state)
        VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET state=excluded.state
    """, (user_id, json.dumps(state, ensure_ascii=False)))
    db.commit()
    db.close()

    return jsonify({"status": "ok"})

@app.route("/save_state", methods=["POST"])
def save_state():
    data = request.get_json(force=True)
    user_id = str(data.get("id"))
    state = data.get("state", {})

    db = get_db()
    db.execute("""
        INSERT INTO players (id, state)
        VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET state=excluded.state
    """, (user_id, json.dumps(state, ensure_ascii=False)))
    db.commit()
    db.close()

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
