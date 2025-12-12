from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# MySQL connection
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="brucewayne@1125",
        database="aiinventorysystem",
        auth_plugin='mysql_native_password'
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    conn = get_db_connection()            # <-- call the function
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT i.id, i.product_id, p.name, i.stock, i.safety_stock, i.lead_time_days from inventory as i join products as p on i.product_id=p.product_id where i.product_id=p.product_id")  # Replace with your table name
    data = cursor.fetchall()
    cursor.close()
    conn.close()                          # <-- close connection
    return render_template('inventory.html', table=data)


@app.route('/sales')
def sales():
    conn = get_db_connection()            # <-- call the function
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.id, s.product_id, p.name, s.quantity, s.sold_at from sales as s join products as p where s.product_id=p.product_id")  # Replace with your table name
    data = cursor.fetchall()
    cursor.close()
    conn.close()                          # <-- close connection
    return render_template('sales.html', table=data)

@app.route('/products')
def products():
    conn = get_db_connection()            # <-- call the function
    cursor = conn.cursor(dictionary=True)
    cursor.execute("select * from products")  # Replace with your table name
    data = cursor.fetchall()
    cursor.close()
    conn.close()                          # <-- close connection
    return render_template('products.html', table=data)

@app.route('/lowstocklog')
def lowstocklog():
    conn = get_db_connection()            # <-- call the function
    cursor = conn.cursor(dictionary=True)
    cursor.execute("select * from low_stock_log")  # Replace with your table name
    data = cursor.fetchall()
    cursor.close()
    conn.close()                          # <-- close connection
    return render_template('lowstocklog.html', table=data)

if __name__ == '__main__':
    app.run(debug=True)
