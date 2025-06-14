from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = "sms.db"

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/api/summary")
def summary():
    # Sum income and expenses by type name
    rows = query_db("""
        SELECT tt.name, SUM(t.amount) as total
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        GROUP BY tt.name
    """)

    total_income = 0
    total_expense = 0
    for row in rows:
        if row["name"].lower() == "income":
            total_income = row["total"] or 0
        elif row["name"].lower() == "expense":
            total_expense = row["total"] or 0

    total_balance = total_income - total_expense

    # Placeholder for change values
    return jsonify({
        "total_balance": total_balance,
        "balance_change": 0,
        "total_income": total_income,
        "income_change": 0,
        "total_expense": total_expense,
        "expense_change": 0
    })

@app.route("/api/recent-transactions")
def recent_transactions():
    rows = query_db("""
        SELECT t.id, t.amount, t.date, tt.name as type, t.sender_name, t.receiver_name
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        ORDER BY date DESC, id DESC
        LIMIT 20
    """)
    result = []
    for r in rows:
        # Splitting date/time for frontend labels (adjust if your date format differs)
        date = r["date"].split(" ")[0]
        time = r["date"].split(" ")[1] if " " in r["date"] else "00:00"
        result.append({
            "id": r["id"],
            "amount": r["amount"],
            "date": date,
            "time": time,
            "type": r["type"],
            "sender_name": r["sender_name"],
            "receiver_name": r["receiver_name"],
            "balance": 0  # If you track balance, else keep 0 or calculate
        })
    return jsonify(result)

@app.route("/api/transaction-types")
def transaction_types():
    rows = query_db("""
        SELECT tt.name as type, SUM(t.amount) as total_amount
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        GROUP BY tt.name
    """)
    result = [{"type": r["type"], "total_amount": r["total_amount"]} for r in rows]
    return jsonify(result)

@app.route("/api/monthly-trends")
def monthly_trends():
    rows = query_db("""
        SELECT 
            substr(t.date, 1, 7) as month, 
            SUM(CASE WHEN tt.name = 'payment' THEN t.amount ELSE 0 END) as payments,
            SUM(CASE WHEN tt.name = 'deposit' THEN t.amount ELSE 0 END) as deposits
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        GROUP BY month
        ORDER BY month
        LIMIT 12
    """)

    months = []
    payments = []
    deposits = []
    for r in rows:
        months.append(r["month"])
        payments.append(r["payments"] or 0)
        deposits.append(r["deposits"] or 0)

    return jsonify({
        "months": months,
        "payments": payments,
        "deposits": deposits
    })

@app.route("/api/volume-by-type")
def volume_by_type():
    rows = query_db("""
        SELECT tt.name as label, COUNT(*) as count
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        GROUP BY tt.name
    """)
    labels = [r["label"] for r in rows]
    data = [r["count"] for r in rows]

    return jsonify({"labels": labels, "data": data})

if __name__ == "__main__":
    app.run(debug=True)
