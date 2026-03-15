from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "steppe_tycoon.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            money INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            money INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
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
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

    if user:
        result = dict(user)
    else:
        db.execute(
            "INSERT INTO users (id, money, level) VALUES (?, ?, ?)",
            (user_id, 0, 1)
        )
        db.commit()
        result = {"id": user_id, "money": 0, "level": 1}

    db.close()
    return jsonify(result)

@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()

    user_id = str(data.get("id"))
    money = int(data.get("money", 0))
    level = int(data.get("level", 1))

    db = get_db()
    db.execute("""
        INSERT INTO users (id, money, level)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            money=excluded.money,
            level=excluded.level
    """, (user_id, money, level))
    db.commit()
    db.close()

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
