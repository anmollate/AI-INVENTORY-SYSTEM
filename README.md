# AI Inventory Management System

An AI-powered inventory management system that analyzes sales data to generate insights such as daily transactions, products sold, and market basket analysis. The system helps in understanding sales patterns and improving inventory decisions.

## Features
- Daily transactions count
- Products sold analytics
- Sales visualizations (bar charts, heatmaps, network graphs)
- Market Basket Analysis (Apriori algorithm)
- Interactive dashboards
- PostgreSQL database integration

## Tech Stack
- Backend: Python, Flask
- Database: PostgreSQL
- Data Analysis: Pandas, MLxtend
- Visualization: Plotly, Matplotlib
- Frontend: HTML, CSS
- Version Control: Git, GitHub

## Project Structure
AI-INVENTORY-SYSTEM
│   .env
│   .gitignore
│   app.py
│   appriori.py
│   README.md
│   requirements.txt
│   salestablegeneration.py
│   sales_dataset_1000_rows.csv
│   sales_dataset_1000_rows1.csv
│
├───static
│       styles.css
│       stylesform.css
│       stylestable.css
│
└───templates
        addproduct.html
        addsales.html
        index.html
        inventory.html
        lowstocklog.html
        products.html
        sales.html
        updateinventory.
        

## Installation & Setup
1. Clone the repository:
```bash
git clone https://github.com/your-username/AI-INVENTORY-SYSTEM.git
cd AI-INVENTORY-SYSTEM

## Install Dependencies
pip install -r requirements.txt

## Run The Application
python app.py

## Use Cases
- Inventory optimization  
- Sales trend analysis  
- Product association insights  
- Business decision support  

## Future Enhancements
- User authentication  
- Product recommendation system  
- Cloud deployment (Render)  
- Real-time analytics dashboard  

## Author
**Anmol Late**  
B.E – Artificial Intelligence & Data Science


