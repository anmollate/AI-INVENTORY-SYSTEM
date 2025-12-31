from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
import plotly.express as px
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# PostgreSQL connection
# def get_db_connection():
#     conn = psycopg2.connect(
#         host=os.getenv("DB_HOST"),
#         database=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASS"),
#         port=os.getenv("DB_PORT", 5432)
#     )
#     return conn

#Render DB Connection
DATABASE_URL = os.environ.get("DATABASE_URL")
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

@app.route('/')
def index():
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    #getting the names and quantity for top selling products
    cursor.execute('select product, sum(quantity) as totalsold from sales group by product order by totalsold DESC limit 10')
    result=cursor.fetchall()
    products=[row['product'] for row in result]
    values=[row['totalsold'] for row in result]
    #plotting graph for top selling products
    fig=px.bar(
        x=products,
        y=values,
        labels={'x':'Products','y':'Quantity Sold'},
        title='Top Selling Products',
        color=values,
        color_continuous_scale=['yellow','green']
    )
    plot_div=fig.to_html(full_html=False)



    #getting the name and quantity for least selling products
    cursor.execute('select product,sum(quantity) as tqty from sales group by product order by tqty limit 10')
    result1=cursor.fetchall()
    lproducts=[row['product'] for row in result1]
    lqty=[row['tqty'] for row in result1]
    #plotting the graph for least selling products
    fig1=px.bar(
        x=lproducts,
        y=lqty,
        labels={'x':'Products','y':'Quantity'},
        title='Least Selling Products',
        color=lqty,
        color_continuous_scale=['red','yellow']
    )
    lplot_div=fig1.to_html(full_html=False)



    #apriori algo top selling combos
    query = """
    SELECT transaction_id, product
    FROM sales
    ORDER BY transaction_id
    """

    df = pd.read_sql(query, conn)

    # Prepare basket
    basket = df.pivot_table(
        index='transaction_id',
        columns='product',
        aggfunc='size',
        fill_value=0
    )
    basket = (basket > 0).astype(bool)

    # Frequent itemsets & rules
    freq_items = apriori(basket, min_support=0.005, use_colnames=True)
    rules = association_rules(freq_items, metric="confidence", min_threshold=0.6)
    rules = rules[rules['lift'] > 1]

    # Keep only one direction
    rules['pair'] = rules.apply(lambda x: frozenset(x['antecedents'] | x['consequents']), axis=1)
    rules = rules.sort_values('confidence', ascending=False).drop_duplicates(subset='pair')

    # Convert frozensets to strings
    rules['antecedent'] = rules['antecedents'].apply(lambda x: list(x)[0])
    rules['consequent'] = rules['consequents'].apply(lambda x: list(x)[0])

    # Create matrix
    heatmap_data = rules.pivot(index='antecedent', columns='consequent', values='confidence').fillna(0)

    # Plotly Heatmap
    fig2 = px.imshow(
        heatmap_data,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=['#fcfc04', '#088404'],  # yellow to green
        labels=dict(x="Consequent", y="Antecedent", color="Confidence"),
        title="Product Association Heatmap (Confidence ≥ 60%)"
    )

    fig2.update_xaxes(side="bottom")
    # fig2.show()
    plot_tsc=fig2.to_html(full_html=False) #tsc=top selling combos


    # Top 10 High Impact Products By Revenue
    cursor.execute('select product, sum(quantity*price) as total_price from sales as s join products as p on s.product_id=p.product_id group by product order by total_price DESC limit 10')
    result_r=cursor.fetchall()
    product=[row['product'] for row in result_r]
    revenue=[row['total_price'] for row in result_r]
    fig3=px.bar(
        x=product,
        y=revenue,
        labels={'x':'Products','y':'Total Revenue'},
        title="Top 10 High Impact Products (By Revenue)",
        color=revenue,
        color_continuous_scale=['yellow','green']
    )
    plot_HIPR=fig3.to_html(full_html=False)

    # Number Of Daily Transactions
    cursor.execute('select count(distinct transaction_id) as dailytrans from sales where sold_at=CURRENT_DATE')
    dailytrans=cursor.fetchone()['dailytrans']

    #Number Of Monthly Transactions
    cursor.execute("select count(distinct transaction_id) as mtrans from sales where DATE_TRUNC('month',sold_at)=DATE_TRUNC('month',CURRENT_DATE) and DATE_TRUNC('year',sold_at)=DATE_TRUNC('year',CURRENT_DATE)")
    monthlytrans=cursor.fetchone()['mtrans']

    #Today's Sales Volume
    cursor.execute("select sum(quantity) as tqty from sales where sold_at=Current_date")
    tqty=cursor.fetchone()['tqty']

    #Today's Revenue
    cursor.execute("select sum(s.quantity*p.price) as revenue from sales as s join products as p on s.product_id=p.product_id where s.sold_at=current_date ")
    trevenue=cursor.fetchone()['revenue']


    return render_template('index.html',plot_div=plot_div,lplot_div=lplot_div,plot_tsc=plot_tsc,plot_HIPR=plot_HIPR,dailytrans=dailytrans,monthlytrans=monthlytrans,tqty=tqty,trevenue=trevenue)

#Route To The Add Sales Page
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

@app.route('/monthlysales')
def monthlysales():
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    return render_template('monthlysales.html')

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

#Inserting The Sales Data Inside The Table
@app.route('/submit', methods=['POST'])
def submit():
    t_id = request.form['tid']
    sold_at = request.form['date']
    # these now come as lists
    products = request.form.getlist('pname[]')
    quantities = request.form.getlist('qty[]')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    for product, qty in zip(products, quantities):
        cursor.execute(
            "SELECT product_id FROM products WHERE name = %s",
            (product,)
        )
        pid = cursor.fetchone()['product_id']

        cursor.execute(
            """
            INSERT INTO sales
            (transaction_id, product, quantity, sold_at, product_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (t_id, product, qty, sold_at, pid)
        )

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

@app.route('/submitinv',methods=['POST'])
def submitinv():
    product=request.form['pname']
    get_stock=int(request.form['upstock'])
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("Select product_id from products where name=%s",(product,))
    pid=cursor.fetchone()['product_id']
    cursor.execute('Select stock from inventory where product_id=%s',(pid,))
    stock=cursor.fetchone()['stock']
    up_stock=stock+get_stock
    cursor.execute('Update Inventory set stock=%s where product_id=%s',(up_stock,pid))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/updateinventory')

#Monthly Transactions Filter
@app.route('/submitmnt',methods=['POST'])
def submitmnt():
    result=request.form['month']
    year=int(result.split('-')[0])
    month=int(result.split('-')[1])
    print(year,month)
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('Select * from sales where EXTRACT(MONTH From sold_at)=%s and EXTRACT(YEAR From sold_at)=%s',(month,year))
    data=cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('monthlysales.html',table=data)

@app.route('/updateinventory')
def updateinventory():
    return render_template('updateinventory.html')

@app.route('/addproduct')
def addproduct():
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('Select COALESCE(max(product_id),0)+1 as pid from products')
    pid=cursor.fetchone()['pid']
    cursor.close()
    conn.close()
    return render_template('addproduct.html',pid=pid)

@app.route('/submitprod',methods=['POST'])
def submitprod():
    conn=get_db_connection()
    cursor=conn.cursor(cursor_factory=RealDictCursor)
    pid=request.form['pid']
    pname=request.form['pname']
    price=request.form['price']
    stock=request.form['stock']
    safetystock=request.form['safetystock']
    ltd=request.form['leadtimedays'] 
    cursor.execute('insert into products(name,price) values(%s,%s)',(pname,price))
    conn.commit()
    cursor.execute('insert into inventory(product_id,stock,safety_stock,lead_time_days) values(%s,%s,%s,%s)',(pid,stock,safetystock,ltd))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/addproduct')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
