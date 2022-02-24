import numpy.polynomial.polynomial as poly
from database import *
import psycopg2
import logging
import os
import numpy as np
import string

# Predefined lists
states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
          'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
          'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
temp_avg_cols = ['id', 'tmp_avg_jan', 'tmp_avg_feb', 'tmp_avg_mar', 'tmp_avg_apr', 'tmp_avg_may', 'tmp_avg_jun',
                 'tmp_avg_jul',
                 'tmp_avg_aug', 'tmp_avg_sep', 'tmp_avg_oct', 'tmp_avg_nov', 'tmp_avg_dec']
temp_max_cols = ['id', 'tmp_max_jan', 'tmp_max_feb', 'tmp_max_mar', 'tmp_max_apr', 'tmp_max_may', 'tmp_max_jun',
                 'tmp_max_jul',
                 'tmp_max_aug', 'tmp_max_sep', 'tmp_max_oct', 'tmp_max_nov', 'tmp_max_dec']
temp_min_cols = ['id', 'tmp_min_jan', 'tmp_min_feb', 'tmp_min_mar', 'tmp_min_apr', 'tmp_min_may', 'tmp_min_jun',
                 'tmp_min_jul',
                 'tmp_min_aug', 'tmp_min_sep', 'tmp_min_oct', 'tmp_min_nov', 'tmp_min_dec']
precip_cols = ['id', 'precip_jan', 'precip_feb', 'precip_mar', 'precip_apr', 'precip_may', 'precip_jun', 'precip_jul',
               'precip_aug', 'precip_sep', 'precip_oct', 'precip_nov', 'precip_dec']
coeff_cols = list(string.ascii_lowercase)

''' Query to get list of ids, county codes, county names, states, and countries from DB'''
def get_county_codes_as_df():
    cols = ['id', 'county_code', 'county_name', 'state', 'country']
    conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password=PASSWORD")
    cur = conn.cursor()
    query = "SELECT * FROM county_codes"
    cur.execute(query)
    res = pd.DataFrame(cur.fetchall(), columns=cols)
    cur.close()
    conn.close()
    return res


''' Wrapper to get weather data split into their respective df (avg, max, min, precip) '''
def get_data_dfs(row):
    # Could use state from for loop...
    # However, want to stay consistent with state recorded in db record
    start_year = 1895
    end_year = 2021
    country = 'US'
    county = row['county_name']
    state = row['state']

    # DB call -> Returns pd.Dataframe
    avg_data_df = get_data_for_single_county(temp_avg_cols, county, state, country, start_year, end_year)
    max_data_df = get_data_for_single_county(temp_max_cols, county, state, country, start_year, end_year)
    min_data_df = get_data_for_single_county(temp_min_cols, county, state, country, start_year, end_year)
    precip_data_df = get_data_for_single_county(precip_cols, county, state, country, start_year, end_year)

    return [avg_data_df, max_data_df, min_data_df, precip_data_df]


''' Get data in x & y format per df '''
def get_xy_data(df):
    x_dates_format = []
    x_data = []
    start_year = int(str(df['id'].iloc[0])[6:])
    end_year = int(str(df['id'].iloc[-1])[6:])

    # range(start_year, end_year) == df.shape[0] (num of rows)
    # Append date formatted
    for i in range(start_year, end_year + 1):
        for j in range(1, 13):
            x_dates_format.append(str(i)[-4:] + '-' + str(j))
            x_data.append(int(str(i)[-4:]) + (j - 1) / 12)

    # Append temp/precip values
    y_data = []
    for i, row in df.iterrows():
        for j in row[1:13]:
            y_data.append(j)

    return [x_data, y_data, x_dates_format]


''' Builds csv for county polynomial coefficents '''
def build_poly_coeffs_for_county_csv(deg, der=0):
    print(f'Degree {deg} Polynomial')

    if deg < 1:
        logging.error('Please enter polynomial degree greater than 0')
        quit(1)

    # Dynamically create column headers from 'a' ... deg
    cols = np.hstack(['State', 'County', coeff_cols[:deg+1]])

    # Always init
    avg_data_rows = []
    max_data_rows = []
    min_data_rows = []
    precip_data_rows = []
    missed_counties = []

    for state in states:
        print(f"Storing sub-dataframe for state: {state}")

        # Get county codes, names, state, country etc..
        county_codes_df = get_county_codes_as_df()

        # Get df that matches current state
        state_df = county_codes_df[(county_codes_df['state'] == state)]
        state_df.reset_index()  # make sure indices pair with number of rows

        for index, row in state_df.iterrows():
            print(f"Building and storing coefficients for county: {row['county_name']}")
            [avg_df, max_df, min_df, precip_df] = get_data_dfs(row)

            # TODO not best conditional, but check if there was no weather data based on county passed in
            if avg_df.empty is True and max_df.empty is True and min_df.empty is True and precip_df.empty is True:
                logging.warning(f'Unable to get weather data for county: {row["county_name"]} state: {row["state"]}')
                missed_counties.append([row['state'], row['county_name'], row['county_code']])
                continue

            # Process data
            [x_avg, y_avg, x_avg_dates] = get_xy_data(avg_df)
            [x_max, y_max, x_max_dates] = get_xy_data(max_df)
            [x_min, y_min, x_min_dates] = get_xy_data(min_df)
            [x_precip, y_precip, x_precip_dates] = get_xy_data(precip_df)

            # Get polynomial coefficents
            avg_coeffs = poly.polyfit(x_avg, y_avg, deg)
            max_coeffs = poly.polyfit(x_max, y_max, deg)
            min_coeffs = poly.polyfit(x_min, y_min, deg)
            precip_coeffs = poly.polyfit(x_precip, y_precip, deg)

            # Dynamically add coefficients (any size)
            avg_data_rows.append(np.hstack([row['state'], row['county_name'], avg_coeffs]))
            max_data_rows.append(np.hstack([row['state'], row['county_name'], max_coeffs]))
            min_data_rows.append(np.hstack([row['state'], row['county_name'], min_coeffs]))
            precip_data_rows.append(np.hstack([row['state'], row['county_name'], precip_coeffs]))

            # Check if derivative order has been passed
            if der > 0:
                # Get derivative coeffs of current degree poly coeffs
                print(f'Calculate and storing the {der} order derivative for county {row["county_name"]}')
                avg_deriv = np.polyder(avg_coeffs, der)
                max_deriv = np.polyder(max_coeffs, der)
                min_deriv = np.polyder(min_coeffs, der)
                precip_deriv = np.polyder(precip_coeffs, der)

                # Append to existing data
                avg_data_rows.append(np.hstack([row['state'], row['county_name'], avg_deriv]))
                max_data_rows.append(np.hstack([row['state'], row['county_name'], max_deriv]))
                min_data_rows.append(np.hstack([row['state'], row['county_name'], min_deriv]))
                precip_data_rows.append(np.hstack([row['state'], row['county_name'], precip_deriv]))

    # After data has been looped and appended to, create new dfs to write to csv
    avg_poly_df = pd.DataFrame(avg_data_rows, columns=cols)
    max_poly_df = pd.DataFrame(max_data_rows, columns=cols)
    min_poly_df = pd.DataFrame(min_data_rows, columns=cols)
    precip_poly_df = pd.DataFrame(precip_data_rows, columns=cols)

    # Write to csv
    avg_poly_df.to_csv(f"{deg}_avg_county_coeffs.csv", sep=',', encoding='utf-8', index=False)
    max_poly_df.to_csv(f"{deg}_max_poly_test.csv", sep=',', encoding='utf-8', index=False)
    min_poly_df.to_csv(f"{deg}_min_poly_test.csv", sep=',', encoding='utf-8', index=False)
    precip_poly_df.to_csv(f"{deg}_precip_poly_test.csv", sep=',', encoding='utf-8', index=False)
    print(f'Successfully wrote polynomial coeffs to csv!')

    # Write all counties missed from line 114-117 check
    if not os.path.exists('missed_counties.txt'):
        print(f'Writing missed counties to text file!')
        with open(f'missed_counties.txt', 'w') as text_file:
            for line in missed_counties:
                text_file.write('state: ' + str(line[0]) + ', county: ' + str(line[1]) + ', county_code: ' + str(line[2]) + '\n')
        print(f'Successfully wrote missed counties to text file!')

if __name__ == '__main__':
    build_poly_coeffs_for_county_csv(3, 1)
