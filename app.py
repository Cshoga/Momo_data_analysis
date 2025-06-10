from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows cross-origin requests from frontend

DB_PATH = "sms.db"

# Endpoint to get all transactions or filter by category
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

# Endpoint to get a summary (total amount) per category
@app.route("/summary")
def get_summary():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    rows = cur.fetchall()
    conn.close()

    return jsonify(rows)

# Optional: endpoint to get monthly summaries
@app.route("/monthly_summary")
def get_monthly_summary():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            substr(date, 1, 7) AS month, 
            category, 
            SUM(amount) 
        FROM transactions 
        GROUP BY month, category
    """)
    rows = cur.fetchall()
    conn.close()

    return jsonify(rows)

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
