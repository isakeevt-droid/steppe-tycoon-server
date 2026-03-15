from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
import sqlite3

def init_db():
    conn = sqlite3.connect("steppe_tycoon.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        money INTEGER,
        level INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()
def get_db():
    conn = sqlite3.connect("game.db")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def home():
    return "Steppe Tycoon API works"
@app.route("/get/<user_id>")
def get_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

    if user:
        return jsonify(dict(user))
    else:
        db.execute("INSERT INTO users (id, money, level) VALUES (?,0,1)", (user_id,))
        db.commit()
        return jsonify({"id":user_id,"money":0,"level":1})

@app.route("/save", methods=["POST"])
def save():
    data = request.json
    db = get_db()

    db.execute(
        "UPDATE users SET money=?, level=? WHERE id=?",
        (data["money"], data["level"], data["id"])
    )
    db.commit()

    return {"status":"ok"}

if __name__ == "__main__":
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id TEXT PRIMARY KEY,
        money INTEGER,
        level INTEGER
    )
    """)
    db.commit()

    app.run(host="0.0.0.0", port=10000)
