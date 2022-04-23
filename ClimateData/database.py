import psycopg2
import csv
import sys
import os
import pandas as pd
from os import listdir
from psycopg2.extensions import AsIs
from psycopg2 import connect
from psycopg2 import OperationalError, errorcodes, errors
from psycopg2 import __version__ as psycopg2_version
from enum import Enum

#Put your postgres password here if different
password = 'PASSWORD'
outputDir = './data/processed/'
debug = False

state_dict = {
    101:"AL", 102:"AZ", 103:"AR", 
    104:"CA", 105:"CO", 106:"CT", 
    107:"DE", 108:"FL", 109:"GA",
    110:"ID", 111:"IL", 112:"IN",          
    113:"IA", 114:"KS", 115:"KY", 
    116:"LA", 117:"ME", 118:"MD", 
    119:"MA", 120:"MI", 121:"MN", 
    122:"MS", 123:"MO", 124:"MT", 
    125:"NE", 126:"NV", 127:"NH", 
    128:"NJ", 129:"NM", 130:"NY",
    131:"NC", 132:"ND", 133:"OH",
    134:"OK", 135:"OR", 136:"PA",
    137:"RI", 138:"SC", 139:"SD",
    140:"TN", 141:"TX", 142:"UT",
    143:"VT", 144:"VA", 145:"WA",
    146:"WV", 147:"WI", 148:"WY"
}

#INTERNAL CALLS---------------------------------------------------------------------
def setup_database():
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    drop_all_tables()
    
    if conn != None:
        cur = conn.cursor()
        filenames = find_csv_filenames(f'{outputDir}')
        for fileName in filenames:
            if fileName != "county_coords.csv":
                tableName  = os.path.basename(fileName).split(".")[0]
                print(f"Creating table: {tableName}")
                with open(f'{outputDir}{fileName}', 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    columns = next(reader)
                columnString = ", ".join(columns)
                try:
                    cur.execute("""
                    CREATE TABLE %s(
                    %s)
                    """,
                    [AsIs(tableName), AsIs(columnString),])
                    conn.commit()
                except Exception as error:
                    if debug == True:
                        print_psycopg2_exception(error)
                    conn.rollback()
                

                with open(f'{outputDir}{fileName}', 'r', encoding='utf-8-sig') as f:
                    next(f)
                    try:
                        cur.copy_from(f, f'{tableName}', sep=',')
                        conn.commit()
                        print(f"{tableName} successfully created")
                    except Exception as error:
                        if debug == True:
                            print_psycopg2_exception(error)
                        else:
                            print("WARNING: Some exception messages were suppressed while creating tables.")
                            print("This will happen if updating the database.")
                            print("Ensure the tables that you are trying to update have printed as successfully created.")
                        conn.rollback()


        cur.close()
        conn.close()
        setup_coordinates_table()

def setup_coordinates_table():
    print("Creating table: county_coords")
    csv.field_size_limit(2147483647)
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        with open(f'{outputDir}county_coords.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=',', quotechar='"')
                columns = next(reader)
                columnString = ", ".join(columns)
                try:
                    cur.execute("""
                    CREATE TABLE county_coords(
                    %s)
                    """,
                    [AsIs(columnString),])
                    conn.commit()
                except Exception as error:
                    if debug == True:
                        print_psycopg2_exception(error)
                    else:
                        print("WARNING: Some exception messages were suppressed while creating coordinates table.")
                        print("This will happen if updating the database.")
                        print("Ensure the tables that you are trying to update have printed as successfully created.")
                    conn.rollback()
                try:
                    for row in reader:
                        statement = "INSERT INTO county_coords " + \
                        "(county_code, geo_point, geo_shape) " + \
                        "VALUES ('%s', '%s', '%s')" % (tuple(row[0:3]))
                        cur.execute(statement)
                        conn.commit()
                    print("county_coords successfully created")
                except Exception as error:
                    if debug == True:
                        print_psycopg2_exception(error)
                    else:
                        print("WARNING: Some exception messages were suppressed. This will happen if updating the database.")
                        print("Ensure the tables that you are trying to update have printed as successfully created.")
                    conn.rollback()
        cur.close()
        conn.close()

def find_csv_filenames(path_to_dir, suffix=".csv"):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def drop_table(tableName):
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None
    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            DROP TABLE %s;
            """,
            [AsIs(tableName),])
            conn.commit()
        except Exception as error:
            if debug == True:
                print_psycopg2_exception(error)
            else:
                print("WARNING: Some exception messages were suppressed while dropping a table.")
                print("This will happen if updating the database.")
                print("Ensure the tables that you are trying to update have printed as successfully created.")
            conn.rollback()
        cur.close()
        conn.close()
        
def drop_all_tables():
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        tableString = "weather, drought, county_codes"

        print("Dropping tables: " + tableString)

        cur = conn.cursor()
        try:
            cur.execute("""
            DROP TABLE %s;
            """,
            [AsIs(tableString),])
            conn.commit()
        except Exception as error:
            if debug == True:
                print_psycopg2_exception(error)
            else:
                print("WARNING: Some exception messages were suppressed while dropping tables.")
                print("This will happen if updating the database.")
                print("Ensure the tables that you are trying to update have printed as successfully created.")
            conn.rollback()
        cur.close()
        conn.close()

def get_postal(county, state, country):
    results = None
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            SELECT fips_code FROM county_codes WHERE county_name = '%s' AND state = '%s' AND country = '%s';
            """,
            [AsIs(county), AsIs(state), AsIs(country)])
            results = cur.fetchone()
        except Exception as error:
            print_psycopg2_exception(error)
    
        cur.close()
        conn.close()
    if results is not None:
        results = str(results[0])
        if len(results)< 5:
            results = f'0{results}'
    else:
        print("No postal fips id was found for given country, state and county")
        results = ""

    return results

def get_id_by_county(county, state, country):
    results = None
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            SELECT county_code FROM county_codes WHERE county_name = '%s' AND state = '%s' AND country = '%s';
            """,
            [AsIs(county), AsIs(state), AsIs(country)])
            results = cur.fetchone()
        except Exception as error:
            print_psycopg2_exception(error)
            
        cur.close()
        conn.close()
    if results is not None:
        results = str(results[0])
        if len(results)< 7:
            results = f'0{results}'
    else:
        print("No id was found for given country, state and county")
        results = ""

    return results

def get_ids_by_state(state, country):
    formatted_results = []
    results = None
    
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            SELECT county_code FROM county_codes WHERE state = '%s' AND country = '%s';
            """,
            [AsIs(state), AsIs(country)])
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)
        
        cur.close()
        conn.close()
    
    if results is not None:
        for row in results:
            if len(str(row[0]))< 7:
                formatted_results.append(f'0{row[0]}')
    else:
        print("No ids were found for given country and state")

    return formatted_results

def get_ids_by_country(country):
    formatted_results = []
    results = None
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()

        try:
            cur.execute("""
            SELECT county_code FROM county_codes WHERE country = '%s';
            """,
            [AsIs(country)])
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)

        cur.close()
        conn.close()
    
    if results is not None:
        for row in results:
            if len(str(row[0]))< 7:
                formatted_results.append(f'0{row[0]}')
    else:
        print("No ids were found for given country")
    
    return formatted_results


def get_weather_data(columnList, idList, startYear, endYear):
    results = None
    cols = []
    matchString = "|| '%'"
    defaultColumns = "id, "
    columnString = ", ".join(columnList)
    idYearList = []
    columnString = defaultColumns + columnString
    
    columnName = columnList[0][:-4]
    print("******** COLUMN NAME: " + columnName)

    if columnName == 'tmp_avg' or columnName == 'tmp_min' or columnName == 'tmp_max' or columnName == 'precip':
        table = "weather"
    else:
        table = "drought"
    print("**********TABLE: " + table)
    for year in range(startYear, endYear+1):
        for dataId in idList:
            idYearList.append(dataId+str(year))

    idString = ", ".join(idYearList)

    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()

        try:
            cur.execute("""
            SELECT %s FROM %s WHERE id in (%s) ORDER BY id ASC;
            """,
            [AsIs(columnString), AsIs(table),  AsIs(idString)])
            conn.commit()
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)

        if results is not None:
            for item in cur.description:
                cols.append(item[0])
        else:
            print("No data found for given columns, ids and years")
        cur.close()
        conn.close()

    df = pd.DataFrame(data=results, columns=cols)
    df.id = df.id.apply('{:0>11}'.format).astype(str)
    return df






def get_map_weather_data(columnList, idList, startYear, endYear):
    results = None
    cols = []
    matchString = "|| '%'"
    defaultColumns = "w.id, cc.fips_code, cc.county_name, cc.state, cc.country, "
    columns = ["w." + col for col in columnList]
    columnString = ", ".join(columns)
    idYearList = []
    columnString = defaultColumns + columnString

    for year in range(startYear, endYear+1):
        for dataId in idList:
            idYearList.append(dataId+str(year))

    idString = ", ".join(idYearList)

    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()

        try:
            cur.execute("""
            SELECT %s FROM weather as w JOIN county_codes as cc 
            ON CAST(w.id AS TEXT) like CAST(cc.county_code AS TEXT) || '%%' WHERE w.id IN (%s) ORDER BY id ASC;
            """,
            [AsIs(columnString), AsIs(idString)])
            conn.commit()
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)

        if results is not None:
            for item in cur.description:
                cols.append(item[0])
        else:
            print("No data found for given columns, ids and years")
        cur.close()
        conn.close()

    df = pd.DataFrame(data=results, columns=cols)
    df.fips_code = df.fips_code.apply('{:0>5}'.format).astype(str)
    return df

def get_map_data_for_single_county(columnList, county, state, country, startYear, endYear):
        idList = []
        idList.append(get_id_by_county(county, state, country))
        return get_map_weather_data(columnList, idList, startYear, endYear)

def get_map_data_for_state(columnList, state, country, startYear, endYear):
        idList = []
        idList = get_ids_by_state(state, country)
        return get_map_weather_data(columnList, idList, startYear, endYear)

def get_map_data_for_country(columnList, country, startYear, endYear):
        idList = []
        idList = get_ids_by_country(country)
        return get_map_weather_data(columnList, idList, startYear, endYear)


def get_data_for_single_county(columnList, county, state, country, startYear, endYear):
        idList = []
        idList.append(get_id_by_county(county, state, country))
        return get_weather_data(columnList, idList, startYear, endYear)

def get_data_for_state(columnList, state, country, startYear, endYear):
        idList = []
        idList = get_ids_by_state(state, country)
        return get_weather_data(columnList, idList, startYear, endYear)

def get_data_for_country(columnList, country, startYear, endYear):
        idList = []
        idList = get_ids_by_country(country)
        return get_weather_data(columnList, idList, startYear, endYear)

def get_coordinates(countyId):
    cols = []
    results = None

    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            SELECT * FROM county_coords
            WHERE county_code = %s;
            """,
            [AsIs(countyId)])
            conn.commit()
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)

        if results is not None:
            for item in cur.description:
                cols.append(item[0])
        cur.close()
        conn.close()
    
    df = pd.DataFrame(data=results, columns=cols)
    return df

def print_psycopg2_exception(error):
    err_type, err_obj, traceback = sys.exc_info()
    line_num = traceback.tb_lineno
    print ("\npsycopg2 ERROR:", error, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)
    print ("\nextensions.Diagnostics:", error.diag)
    print ("pgerror:", error.pgerror)
    print ("pgcode:", error.pgcode, "\n")
    




#EXTERNAL CALLS---------------------------------------------------------------------
def get_ids_for_counties_list(states, counties, country):
    idsList = []
    stateList = []
    countyList = []
    countryList = []
    for index, state in enumerate(states):
        for county in counties[index]:
            id_to_add = get_id_by_county(county, state, country)
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

def get_postal_fips(states, counties, country):
    idsList = []
    postalFips = []
    stateList = []
    countyList = []
    countryList = []

    for index, state in enumerate(states):
        for county in counties[index]:
            id_to_add = get_id_by_county(county, state, country)
            postal_to_add = get_postal(county, state, country)
            postalFips.append(postal_to_add)
            idsList.append(id_to_add)
            stateList.append(state)
            countyList.append(county)
            countryList.append(country)

    results = pd.DataFrame(idsList, columns=["id"])
    results['PostalFips'] = postalFips
    results['County'] = countyList
    results['State'] = stateList
    results['Country'] = countryList
    return results

def get_map_data_for_counties(states, counties, country, columns, months, startYear, endYear):
    results = []
    columnList = []
    idList = []

    for column in columns:
        for month in months:
            to_add = column + '_' + month.lower()
            columnList.append(to_add)

    for index, state in enumerate(states):
        for county in counties:
            idList.append(get_id_by_county(county, state, country))
    
    results = get_map_weather_data(columnList, idList, startYear, endYear)
    return results

def get_map_data_for_states(states, country, columns, months, startYear, endYear):
    results = []
    columnList = []
    idList = []
    ids = []

    for column in columns:
        for month in months:
            to_add = column + '_' + month.lower()
            columnList.append(to_add)

    for state in states:
        ids = ids + get_ids_by_state(state, country)
        
    results = get_map_weather_data(columnList, ids, startYear, endYear)

    return results

def get_map_data_for_countries(countries, columns, months, startYear, endYear):
    results = []
    columnList = []
    ids = []

    for column in columns:
        for month in months:
            to_add = column + '_' + month.lower()
            columnList.append(to_add)

    for country in countries:
        ids = ids + get_ids_by_country(country)

    results = get_map_weather_data(columnList, ids, startYear, endYear)

    return results

def get_data_for_counties_dataset(states, counties, country, columns, months, startYear, endYear):
    results = []
    columnList = []

    for column in columns:
        for month in months:
            to_add = column + '_' + month.lower()
            columnList.append(to_add)

    for index, state in enumerate(states):
        for county in counties[index]:
            next_set = get_data_for_single_county(columnList, county, state, country, startYear, endYear)
            results.append(next_set)
    return results

def get_data_for_states_dataset(states, country, columns, months, startYear, endYear):
    results = []
    columnList = []

    for column in columns:
        for month in months:
            to_add = column + '_' + month.lower()
            columnList.append(to_add)

    for state in states:
        next_set = get_data_for_state(columnList, state, country, startYear, endYear)
        results.append(next_set)
    return results

def get_data_for_countries_dataset(countries, columns, months, startYear, endYear):
    results = []
    columnList = []

    for column in columns:
        for month in months:
            to_add = column + '_' + month.lower()
            columnList.append(to_add)

    for country in countries:
        next_set = get_data_for_country(columnList, country, startYear, endYear)
        results.append(next_set)
    return results

def get_counties_for_state(state):
    results = None
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            SELECT county_name FROM county_codes WHERE state = %s;
            """,
            [state])
            conn.commit()
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)
            
        cur.close()
        conn.close()
    if results is None:
        print("No county was found for given state")
        results = ""

    return results


def get_selected_counties_for_state(state, county):
    results = None
    try:
        conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
    except OperationalError as error:
        print_psycopg2_exception(error)
        conn = None

    if conn != None:
        cur = conn.cursor()
        try:
            cur.execute("""
            SELECT state, county_name, county_code, country FROM county_codes WHERE county_name = %s AND state = %s;
            """,
            [county, state])
            conn.commit()
            results = cur.fetchall()
        except Exception as error:
            print_psycopg2_exception(error)

        cur.close()
        conn.close()
    if results is None:
        print("No counties were found for given state and counties")
        results = ""
    
    return results

#if __name__ == "__main__":
#    setup_database()



setup_database()
tartMonth = 'jan'
#convertedStartMonth = Months[startMonth.upper()].value
#print(convertedStartMonth)
endMonth = 'jun'
#for i in range(Months[startMonth.upper()].value, Months[endMonth.upper()].value+1):
#    print(Months(i).name.lower())
columns = ["phdist"]
idList = ["0101001", "0101005"]
startYear = 1900
endYear = 2020
county = "Baldwin"
state = "AL"
country = "US"
countries = ["US"]
states = ["AL", "OR", "WA"]
counties = []
alabama = ["Baldwin", "Bibb", "Calhoun"]
oregon = ["Linn", "Lane", "Multnomah"]
washington = ["Clark", "Cowlitz", "Grant"]
counties.append(alabama)
counties.append(oregon)
counties.append(washington)
months = ['jan', 'feb']
#results = get_data_for_counties_dataset(states, counties, country, columns, months, startYear, endYear)
#results =get_data_for_states_dataset(states, country, columns, startMonth, endMonth, startYear, endYear)
#results = get_data_for_countries_dataset(countries, columns, startMonth, endMonth, startYear, endYear)
#results = get_map_data_for_counties(states, counties, country, columns, startMonth, endMonth, startYear, endYear)
#results = get_map_data_for_states(states, country, columns, startMonth, endMonth, startYear, endYear)
#results = get_map_data_for_countries(countries, columns, startMonth, endMonth, startYear, endYear)
#for result in results:
#    print(results)
