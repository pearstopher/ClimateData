import psycopg2
import csv
import os
from os import listdir
import json
from psycopg2.extensions import AsIs


outputDir = './data/processed/'


def setup_database():
    filenames = find_csv_filenames(f'{outputDir}')
    for fileName in filenames:
        print(fileName)
        tableName  = os.path.basename(fileName).split(".")[0]
        print(tableName)

        with open(f'{outputDir}{fileName}', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            columns = next(reader)
        column_string = ", ".join(columns)
        print(column_string)
        
        conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE %s(
        %s)
        """,
        [AsIs(tableName), AsIs(column_string),])
        print(cur.rowcount)
        conn.commit()

        with open(f'{outputDir}{fileName}', 'r', encoding='utf-8-sig') as f:
            next(f) # Skip the header row.
            cur.copy_from(f, f'{tableName}', sep=',')
        conn.commit()

def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]




setup_database()
