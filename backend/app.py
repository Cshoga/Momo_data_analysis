from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
from datetime import datetime, timedelta
from urllib.parse import unquote_plus
import os

app = Flask(__name__)
CORS(app) 

def get_db_connection():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    db_path = os.path.join(root_dir, "momo.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/api/overview")
def get_overview():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) as count, SUM(amount) as total
        FROM transactions
        WHERE source = 'Mobile'
    """)
    total_stats = cur.fetchone()
    
    cur.execute("""
        SELECT 
            SUM(CASE WHEN tt.name IN ('Incoming Money', 'Bank Deposits') THEN amount ELSE 0 END) as incoming,
            SUM(CASE WHEN tt.name NOT IN ('Incoming Money', 'Bank Deposits', 'Uncategorized') THEN amount ELSE 0 END) as outgoing
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        WHERE t.source = 'Mobile'
    """)
    money_flow = cur.fetchone()
    
    last_month = datetime.now() - timedelta(days=30)
    cur.execute("""
        SELECT COUNT(*) as count, SUM(amount) as total
        FROM transactions
        WHERE date >= ? AND source = 'Mobile'
    """, (last_month.strftime('%Y-%m-%d'),))
    last_month_stats = cur.fetchone()
    
    conn.close()
    
   
    total_count = total_stats[0] or 0
    total_amount = total_stats[1] or 0
    last_month_count = last_month_stats[0] or 0
    last_month_amount = last_month_stats[1] or 0

    
    count_trend = ((total_count - last_month_count) / last_month_count * 100) if last_month_count > 0 else 0
    amount_trend = ((total_amount - last_month_amount) / last_month_amount * 100) if last_month_amount > 0 else 0
    
    return jsonify({
        "total_transactions": total_count,
        "total_volume": total_amount,
        "incoming_money": money_flow[0] or 0,
        "outgoing_money": money_flow[1] or 0,
        "trends": {
            "transactions": count_trend,
            "volume": amount_trend
        }
    })

@app.route("/api/category-distribution")
def get_category_distribution():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            tt.name as category,
            COUNT(*) as transaction_count,
            SUM(t.amount) as total_amount
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        GROUP BY tt.name
        ORDER BY total_amount DESC
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    columns = [description[0] for description in cur.description]
    return jsonify([dict(zip(columns, row)) for row in rows])

@app.route("/api/transactions")
def get_paginated_transactions():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    category = request.args.get('category')
    if category:
        category = unquote_plus(category.strip())
    
    sort_by = request.args.get('sort_by', 'date')
    sort_order = request.args.get('sort_order', 'desc')
    
    valid_sort_columns = ['date', 'amount', 'transaction_id']
    if sort_by not in valid_sort_columns:
        sort_by = 'date'
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'
    
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cur = conn.cursor()
   
    base_query = """
        FROM transactions t
        LEFT JOIN transaction_types tt ON t.type_id = tt.id
        LEFT JOIN agents a ON t.agent_id = a.id
    """
    where_clause = ""
    params = []
    if category:
        where_clause = " WHERE LOWER(tt.name) = LOWER(?)"
        params.append(category)
    
   
    count_query = f"SELECT COUNT(*) {base_query}{where_clause}"
    cur.execute(count_query, params)
    total_count = cur.fetchone()[0]
    
    query = f"""
        SELECT 
            t.*, 
            tt.name as category, 
            a.name as agent_name,
            CASE 
                WHEN tt.name = 'Bank Deposits' THEN 'Mobile Money'
                WHEN tt.name IN ('Incoming Money') THEN t.sender_name
                WHEN tt.name IN ('Payments to Code Holders', 'Transfers to Mobile Numbers') THEN t.receiver_name
                ELSE t.receiver_name
            END as counterparty_name,
            CASE 
                WHEN tt.name = 'Incoming Money' THEN 'sender'
                ELSE 'receiver'
            END as counterparty_type
        {base_query}
        {where_clause}
        ORDER BY t.{sort_by} {sort_order}
        LIMIT ? OFFSET ?
    """
    
    params.extend([per_page, offset])
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    columns = [description[0] for description in cur.description]
    transactions = [dict(zip(columns, row)) for row in rows]
    
    return jsonify({
        "transactions": transactions,
        "pagination": {
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page
        }
    })

@app.route("/api/time-analysis")
def get_time_analysis():
    period = request.args.get('period', 'daily')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if period == 'daily':
        cur.execute("""
            SELECT 
                strftime('%Y-%m-%d', date) as date,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount
            FROM transactions
            GROUP BY strftime('%Y-%m-%d', date)
            ORDER BY date DESC
            LIMIT 30
        """)
    elif period == 'monthly':
        cur.execute("""
            SELECT 
                strftime('%Y-%m', date) as month,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount
            FROM transactions
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
            LIMIT 12
        """)
    else:
        return jsonify({"error": "Invalid period"}), 400
    
    rows = cur.fetchall()
    conn.close()
    
    columns = [description[0] for description in cur.description]
    return jsonify([dict(zip(columns, row)) for row in rows])

@app.route("/api/recent-transactions")
def get_transactions():
    category = request.args.get("category")
    query = """
        SELECT t.*, tt.name as category, a.name as agent_name 
        FROM transactions t
        LEFT JOIN transaction_types tt ON t.type_id = tt.id
        LEFT JOIN agents a ON t.agent_id = a.id
    """
    params = []

    if category:
        query += " WHERE tt.name = ?"
        params.append(category)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    columns = [description[0] for description in cur.description]
    return jsonify([dict(zip(columns, row)) for row in rows])

@app.route("/api/stats")
def get_summary():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        SELECT tt.name as category, SUM(t.amount) as total_amount 
        FROM transactions t
        JOIN transaction_types tt ON t.type_id = tt.id
        GROUP BY tt.name
    """)
    rows = cur.fetchall()
    conn.close()

    columns = [description[0] for description in cur.description]
    return jsonify([dict(zip(columns, row)) for row in rows])

if __name__ == "__main__":
    app.run(debug=True)
