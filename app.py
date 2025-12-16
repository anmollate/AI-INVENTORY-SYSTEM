from flask import Flask, render_template, request, redirect
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

@app.route('/addsales')
def addsales():
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""Select COALESCE(max(transaction_id),0)+1 as nextid from sales""")
    next_id=cursor.fetchone()['nextid'] 
    # ['nextid'] because it .fetchone() returns a dict-> {'nextid':101}
    cursor.close()
    conn.close()
    return render_template('addsales.html',next_id=next_id)

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT i.id, i.product_id, p.name,
               i.stock, i.safety_stock, i.lead_time_days
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        Order By i.id
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
        SELECT  s.transaction_id,s.product_id, p.name,
               s.quantity, s.sold_at
        FROM sales s
        JOIN products p ON s.product_id = p.product_id order by s.transaction_id,s.sold_at,s.product_id
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sales.html', table=data)

@app.route('/submit',methods=['POST'])
def submit():
    t_id=request.form['tid']
    product=request.form['pname']
    sold_at=request.form['date']
    qty=request.form['qty']
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""Select product_id from products where name=%s""",(product,))
    pid=cursor.fetchone()['product_id']
    # print(result)
    cursor.execute("Insert Into sales(transaction_id,product,quantity,sold_at,product_id) values(%s,%s,%s,%s,%s)",(t_id,product,qty,sold_at,pid))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/addsales')

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
