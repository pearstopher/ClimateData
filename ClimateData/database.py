import psycopg2
import csv
import os
from os import listdir
from psycopg2.extensions import AsIs


#Put your postgres password here if different
password = 'PASSWORD'
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
        columnString = ", ".join(columns)
        print(columnString)
        
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE %s(
        %s)
        """,
        [AsIs(tableName), AsIs(columnString),])
        conn.commit()

        with open(f'{outputDir}{fileName}', 'r', encoding='utf-8-sig') as f:
            next(f) # Skip the header row.
            cur.copy_from(f, f'{tableName}', sep=',')
        conn.commit()

        cur.close()
        conn.close()


def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]


def drop_table(tableName):
    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    DROP TABLE %s;
    """,
    [AsIs(tableName),])
    conn.commit()
    cur.close()
    conn.close()
    

#tableName, columnList and idList must be sent in as strings or lists of strings
def get_data(tableName, columnList, idList, startYear, endYear):
    columnString = ", ".join(columnList)
    idYearList = []
    
    for year in range(startYear, endYear+1):
        for dataId in idList:
            idYearList.append(dataId+str(year))
        
    idString = ", ".join(idYearList)

    print("Fetching ids: ")
    print(idYearList)

    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    SELECT %s FROM %s WHERE id IN (%s);
    """,
    [AsIs(columnString), AsIs(tableName), AsIs(idString)])
    conn.commit()
    results = cur.fetchall()
    cur.close()
    conn.close()
    for row in results:
        print(row)
    return results


setup_database()

tableName = "weather"
columnList = ["id", "tmp_avg_jan"]
idList = ["0101001", "0101005"]
startYear = 1990
endYear = 1995

#get_data(tableName, columnList, idList, startYear, endYear)
