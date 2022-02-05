import psycopg2
import csv


def setup_database():
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE climate_data(
        id INTEGER PRIMARY KEY,
        "tmp-avg-Jan" FLOAT, 
        "tmp-avg-Feb" FLOAT,
        "tmp-avg-Mar" FLOAT,
        "tmp-avg-Apr" FLOAT,
        "tmp-avg-May" FLOAT,
        "tmp-avg-Jun" FLOAT,
        "tmp-avg-Jul" FLOAT,
        "tmp-avg-Aug" FLOAT,
        "tmp-avg-Sep" FLOAT,
        "tmp-avg-Oct" FLOAT,
        "tmp-avg-Nov" FLOAT,
        "tmp-avg-Dec" FLOAT,
        "tmp-max-Jan" FLOAT,
        "tmp-max-Feb" FLOAT,
        "tmp-max-Mar" FLOAT,
        "tmp-max-Apr" FLOAT,
        "tmp-max-May" FLOAT,
        "tmp-max-Jun" FLOAT,
        "tmp-max-Jul" FLOAT,
        "tmp-max-Aug" FLOAT,
        "tmp-max-Sep" FLOAT,
        "tmp-max-Oct" FLOAT,
        "tmp-max-Nov" FLOAT,
        "tmp-max-Dec" FLOAT,
        "tmp-min-Jan" FLOAT,
        "tmp-min-Feb" FLOAT,
        "tmp-min-Mar" FLOAT,
        "tmp-min-Apr" FLOAT,
        "tmp-min-May" FLOAT,
        "tmp-min-Jun" FLOAT,
        "tmp-min-Jul" FLOAT,
        "tmp-min-Aug" FLOAT,
        "tmp-min-Sep" FLOAT,
        "tmp-min-Oct" FLOAT,
        "tmp-min-Nov" FLOAT,
        "tmp-min-Dec" FLOAT,
        "precip-Jan" FLOAT,
        "precip-Feb" FLOAT,
        "precip-Mar" FLOAT,
        "precip-Apr" FLOAT,
        "precip-May" FLOAT,
        "precip-Jun" FLOAT,
        "precip-Jul" FLOAT,
        "precip-Aug" FLOAT,
        "precip-Sep" FLOAT,
        "precip-Oct" FLOAT,
        "precip-Nov" FLOAT,
        "precip-Dec" FLOAT
    )
    """)
    conn.commit()

def load_data():
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
    cur = conn.cursor()
    with open('./data/processed/complete.csv', 'r') as f:
        next(f) # Skip the header row.
        cur.copy_from(f, 'climate_data', sep=',')
    conn.commit()


load_data()
