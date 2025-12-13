from flask import Flask, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# PostgreSQL connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", 5432)
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT i.id, i.product_id, p.name,
               i.stock, i.safety_stock, i.lead_time_days
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('inventory.html', table=data)

@app.route('/sales')
def sales():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT s.id, s.product_id, p.name,
               s.quantity, s.sold_at
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sales.html', table=data)

@app.route('/products')
def products():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('products.html', table=data)

@app.route('/lowstocklog')
def lowstocklog():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM low_stock_log")
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('lowstocklog.html', table=data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
