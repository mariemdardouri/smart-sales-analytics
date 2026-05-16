import psycopg2

conn = psycopg2.connect(
    dbname="SmartSale",
    user="postgres",
    password="chaima",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()