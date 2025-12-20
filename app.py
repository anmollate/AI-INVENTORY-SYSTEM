import pandas as pd
import psycopg2
from mlxtend.frequent_patterns import apriori, association_rules
import plotly.express as px

# Connect to DB and fetch data
conn = psycopg2.connect(
    host='localhost',
    database='AI-INVENTORY_SYSTEM2',
    user='postgres',
    password='brucewayne@1125'
)

query = """
SELECT transaction_id, product
FROM sales
ORDER BY transaction_id
"""

df = pd.read_sql(query, conn)
conn.close()

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
fig = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    color_continuous_scale='YlGn',  # yellow to green
    labels=dict(x="Consequent", y="Antecedent", color="Confidence"),
    title="Product Association Heatmap (Confidence ≥ 60%)"
)

fig.update_xaxes(side="bottom")
fig.show()
