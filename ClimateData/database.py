import psycopg2
import csv
import os
import pandas as pd
from os import listdir
from psycopg2.extensions import AsIs

#Put your postgres password here if different
password = 'PASSWORD'
outputDir = './data/processed/'

#INTERNAL CALLS---------------------------------------------------------------------
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
            next(f)
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
    
def drop_all_tables():
    filenames = find_csv_filenames(f'{outputDir}')
    tableNames = []
    for fileName in filenames:
        tableNames.append(os.path.basename(fileName).split(".")[0])

    tableString = ", ".join(tableNames)
    print("Dropping tables: " + tableString)

    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    DROP TABLE %s;
    """,
    [AsIs(tableString),])
    conn.commit()
    cur.close()
    conn.close()

def get_id_by_county(county, state, country):
    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    SELECT county_code FROM county_codes WHERE county_name = '%s' AND state = '%s' AND country = '%s';
    """,
    [AsIs(county), AsIs(state), AsIs(country)])
    conn.commit()
    results = cur.fetchone()
    
    if results is not None:
        results = str(results[0])
        if len(results)< 7:
            results = f'0{results}'
    else:
        print("No id was found for given country, state and county") 
        results = ""
    cur.close()
    conn.close()
    return results

def get_ids_by_state(state, country):
    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    SELECT county_code FROM county_codes WHERE state = '%s' AND country = '%s';
    """,
    [AsIs(state), AsIs(country)])
    conn.commit()
    results = cur.fetchall()
    formatted_results = []
    if cur.rowcount != 0:
        for row in results:
            if len(str(row[0]))< 7:
                formatted_results.append(f'0{row[0]}')
    else:
        print("No ids were found for given country and state")

    cur.close()
    conn.close()
    return formatted_results

def get_ids_by_country(country):
    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    SELECT county_code FROM county_codes WHERE country = '%s';
    """,
    [AsIs(country)])
    conn.commit()
    results = cur.fetchall()
    formatted_results = []
    if cur.rowcount != 0:
        for row in results:
            if len(str(row[0]))< 7:
                formatted_results.append(f'0{row[0]}')
    else:
        print("No ids were found for given country")

    cur.close()
    conn.close()
    return formatted_results

#tableName, columnList and idList must be sent in as strings or lists of strings. Years are integers. 
def get_data(columnList, idList, startYear, endYear):
    matchString = "|| '%'"
    defaultColumns = ", cc.county_name, cc.state, cc.country"
    columns = ["w." + col for col in columnList]
    columnString = ", ".join(columns)
    idYearList = []
    columnString = columnString + defaultColumns
    
    for year in range(startYear, endYear+1):
        for dataId in idList:
            idYearList.append(dataId+str(year))
        
    idString = ", ".join(idYearList)

    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    cur = conn.cursor()
    cur.execute("""
    SELECT %s FROM weather as w JOIN county_codes as cc 
    ON CAST(w.id AS TEXT) like CAST(cc.county_code AS TEXT) || '%%' WHERE w.id IN (%s);
    """,
    [AsIs(columnString), AsIs(idString)])
    conn.commit()
    results = cur.fetchall()
    cols = []
    for item in cur.description:
        cols.append(item[0])
    cur.close()
    conn.close()
    df = pd.DataFrame(data=results, columns=cols)

    return df

def get_data_for_single_county(columnList, county, state, country, startYear, endYear):
        idList = []
        idList.append(get_id_by_county(county, state, country))
        return get_data(columnList, idList, startYear, endYear)

def get_data_for_state(columnList, state, country, startYear, endYear):
        idList = []
        idList = get_ids_by_state(state, country)
        return get_data(columnList, idList, startYear, endYear)

def get_data_for_country(columnList, country, startYear, endYear):
        idList = []
        idList = get_ids_by_country(country)
        return get_data(columnList, idList, startYear, endYear)



#EXTERNAL CALLS---------------------------------------------------------------------
def get_ids_for_counties_list(states, counties, country):
    idsList = []
    stateList = []
    countyList = []
    countryList = []
    for index, state in enumerate(states):
        for county in counties[index]:
            id_to_add = get_id(county, state, country)
            idsList.append(id_to_add)
            stateList.append(state)
            countyList.append(county)
            countryList.append(country)

    results = pd.DataFrame(idsList, columns=["id"])
    results['County'] = countyList
    results['State'] = stateList
    results['Country'] = countryList
    return results

def get_ids_for_states_list(states, country):
    idsList = []
    stateList = []
    countryList = []
    for index, state in enumerate(states):
        ids_to_add = get_ids_by_state(state, country)
        for index, countyId in enumerate(ids_to_add):
            idsList.append(ids_to_add[index])
            stateList.append(state)
            countryList.append(country)

    results = pd.DataFrame(idsList, columns=["id"])
    results['State'] = stateList
    results['Country'] = countryList
    return results

def get_ids_for_countries_list(countries):
    idsList = []
    countryList = []
    for index, country in enumerate(countries):
        ids_to_add = get_ids_by_country(country)
        for index, countyId in enumerate(ids_to_add):
            idsList.append(ids_to_add[index])
            countryList.append(country)

    results = pd.DataFrame(idsList, columns=["id"])
    results['Country'] = countryList
    return results

def get_data_for_counties_dataset(states, counties, country, columnlist, startyear, endyear):
    results = []
    for index, state in enumerate(states):
        for county in counties[index]:
            next_set = get_data_for_single_county(columnList, county, state, country, startYear, endYear)
            results.append(next_set)
    return results

def get_data_for_states_dataset(states, country, columnList, startYear, endYear):
    results = []
    for state in states:
        next_set = get_data_for_state(columnList, state, country, startYear, endYear)
        results.append(next_set)
    return results

def get_data_for_countries_dataset(countries, columnList, startYear, endYear):
    results = []
    for country in countries:
        next_set = get_data_for_country(columnList, country, startYear, endYear)
        results.append(next_set)
    return results

