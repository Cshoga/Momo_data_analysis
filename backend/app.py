from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

DB_PATH = "sms.db"

@app.route("/transactions")
def get_transactions():
    category = request.args.get("category")
    query = "SELECT * FROM transactions"
    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return jsonify(rows)

@app.route("/summary")
def get_summary():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    rows = cur.fetchall()
    conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)
