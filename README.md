# AI Inventory Management System

An AI-powered inventory management system that analyzes sales data to
generate insights such as daily transactions, products sold, and market
basket analysis. The system helps understand sales patterns and supports
better inventory decisions.

## Features

-   Daily transactions count
-   Products sold analytics
-   Sales visualizations (bar charts, heatmaps, network graphs)
-   Market Basket Analysis (Apriori algorithm)
-   Interactive dashboards
-   PostgreSQL database integration

## Tech Stack

-   Backend: Python, Flask
-   Database: PostgreSQL
-   Data Analysis: Pandas, MLxtend
-   Visualization: Plotly, Matplotlib
-   Frontend: HTML, CSS
-   Version Control: Git, GitHub

## Project Structure

AI-INVENTORY-SYSTEM\
│ .env\
│ .gitignore\
│ app.py\
│ apriori.py\
│ README.md\
│ requirements.txt\
│ salestablegeneration.py\
│ sales_dataset_1000_rows.csv\
│ sales_dataset_1000_rows1.csv

├── static\
│ styles.css\
│ stylesform.css\
│ stylestable.css

└── templates\
addproduct.html\
addsales.html\
index.html\
inventory.html\
lowstocklog.html\
products.html\
sales.html\
updateinventory.html

## Installation & Setup

1.  Clone the repository: git clone
    https://github.com/anmollate/AI-INVENTORY-SYSTEM.git\
    cd AI-INVENTORY-SYSTEM

2.  Install dependencies: pip install -r requirements.txt

3.  Configure environment variables:

-   Create a .env file
-   Add PostgreSQL credentials and Flask config

4.  Run the application: python app.py

## Use Cases

-   Inventory optimization
-   Sales trend analysis
-   Product association insights
-   Business decision support

## Author

Anmol Late\
B.E -- Artificial Intelligence & Data Science
