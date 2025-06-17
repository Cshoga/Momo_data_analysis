from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
from datetime import datetime, timedelta
from urllib.parse import unquote_plus
import os

app = Flask(__name__)
CORS(app)

def get_db():
    """Get db connection with error handling"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "momo.db")
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None):
    """Execute query and return results"""
    try:
        with get_db() as conn:
            return conn.execute(query, params or []).fetchall()
    except Exception as e:
        print(f"Query error: {e}")
        raise

@app.route("/api/overview")
def get_overview():
    try:
        # Total statistics
        total = execute_query("SELECT COUNT(*) as count, SUM(amount) as total FROM transactions WHERE source = 'Mobile'")[0]
        
        # Money flow
        flow = execute_query("""
            SELECT 
                SUM(CASE WHEN tt.name IN ('Incoming Money', 'Bank Deposits') THEN amount ELSE 0 END) as incoming,
                SUM(CASE WHEN tt.name NOT IN ('Incoming Money', 'Bank Deposits', 'Uncategorized') THEN amount ELSE 0 END) as outgoing
            FROM transactions t JOIN transaction_types tt ON t.type_id = tt.id WHERE t.source = 'Mobile'
        """)[0]
        
        # last month
        last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        month_stats = execute_query("SELECT COUNT(*) as count, SUM(amount) as total FROM transactions WHERE date >= ? AND source = 'Mobile'", [last_month])[0]
        
        # Calculate trends
        total_count, total_amount = total['count'] or 0, total['total'] or 0
        month_count, month_amount = month_stats['count'] or 0, month_stats['total'] or 0
        
        return jsonify({
            "total_transactions": total_count,
            "total_volume": total_amount,
            "incoming_money": flow['incoming'] or 0,
            "outgoing_money": flow['outgoing'] or 0,
            "trends": {
                "transactions": ((total_count - month_count) / month_count * 100) if month_count > 0 else 0,
                "volume": ((total_amount - month_amount) / month_amount * 100) if month_amount > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/category-distribution")
def get_category_distribution():
    try:
        rows = execute_query("""
            SELECT tt.name as category, COUNT(*) as transaction_count, SUM(t.amount) as total_amount
            FROM transactions t JOIN transaction_types tt ON t.type_id = tt.id
            GROUP BY tt.name ORDER BY total_amount DESC
        """)
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/api/transactions")
def get_paginated_transactions():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Vallidating inputs
        if sort_by not in ['date', 'amount', 'transaction_id']:
            sort_by = 'date'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        offset = (page - 1) * per_page
        base_query = "FROM transactions t LEFT JOIN transaction_types tt ON t.type_id = tt.id LEFT JOIN agents a ON t.agent_id = a.id"
        where_clause = ""
        params = []
        
        if category:
            category = unquote_plus(category.strip())
            where_clause = " WHERE LOWER(tt.name) = LOWER(?)"
            params.append(category)
        
        # Get total count
        total_count = execute_query(f"SELECT COUNT(*) {base_query}{where_clause}", params)[0][0]
        
        # Get transaactions data
        query = f"""
            SELECT t.*, tt.name as category, a.name as agent_name,
                CASE 
                    WHEN tt.name = 'Bank Deposits' THEN 'Mobile Money'
                    WHEN tt.name = 'Incoming Money' THEN t.sender_name
                    ELSE t.receiver_name
                END as counterparty_name,
                CASE WHEN tt.name = 'Incoming Money' THEN 'sender' ELSE 'receiver' END as counterparty_type
            {base_query}{where_clause}
            ORDER BY t.{sort_by} {sort_order} LIMIT ? OFFSET ?
        """
        
        rows = execute_query(query, params + [per_page, offset])
        
        return jsonify({
            "transactions": [dict(row) for row in rows],
            "pagination": {
                "total": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/time-analysis")
def get_time_analysis():
    try:
        period = request.args.get('period', 'daily')
        
        if period == 'daily':
            query = """
                SELECT strftime('%Y-%m-%d', date) as date, COUNT(*) as transaction_count, SUM(amount) as total_amount
                FROM transactions GROUP BY strftime('%Y-%m-%d', date) ORDER BY date DESC LIMIT 30
            """
        elif period == 'monthly':
            query = """
                SELECT strftime('%Y-%m', date) as month, COUNT(*) as transaction_count, SUM(amount) as total_amount
                FROM transactions GROUP BY strftime('%Y-%m', date) ORDER BY month DESC LIMIT 12
            """
        else:
            return jsonify({"error": "Invalid period"}), 400
        
        rows = execute_query(query)
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/recent-transactions")
def get_recent_transactions():
    try:
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
        
        query += " ORDER BY t.date DESC LIMIT 50"
        rows = execute_query(query, params)
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
def get_stats():
    try:
        rows = execute_query("""
            SELECT tt.name as category, SUM(t.amount) as total_amount 
            FROM transactions t JOIN transaction_types tt ON t.type_id = tt.id
            GROUP BY tt.name
        """)
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test-db")
def test_db():
    try:
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        return jsonify({"status": "success", "tables": [t[0] for t in tables]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
