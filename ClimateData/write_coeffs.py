import numpy as np
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
import pandas as pd
import pandas.io.sql as pdsql
from database import *
import psycopg2
import csv
from psycopg2.extensions import AsIs

'''
interact with db
get polynomial
get derivative
write to csv
'''
# Predefined lists
start_year = '1895'
end_year = '2021'
country = 'US'
states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
# temp_avg_cols = ['tmp_avg_jan', 'tmp_avg_feb', 'tmp_avg_mar', 'tmp_avg_apr', 'tmp_avg_jun', 'tmp_avg_jul',
#                  'tmp_avg_aug', 'tmp_avg_sep', 'tmp_avg_oct', 'tmp_avg_nov', 'tmp_avg_dec']
# temp_max_cols = ['tmp_max_jan', 'tmp_max_feb', 'tmp_max_mar', 'tmp_max_apr', 'tmp_max_jun', 'tmp_max_jul',
#                  'tmp_max_aug', 'tmp_max_sep', 'tmp_max_oct', 'tmp_max_nov', 'tmp_max_dec']
# temp_min_cols = ['tmp_min_jan', 'tmp_min_feb', 'tmp_min_mar', 'tmp_min_apr', 'tmp_min_jun', 'tmp_min_jul',
#                  'tmp_min_aug', 'tmp_min_sep', 'tmp_min_oct', 'tmp_min_nov', 'tmp_min_dec']
# precip_cols = ['precip_jan', 'precip_feb', 'precip_mar', 'precip_apr', 'precip_jun', 'precip_jul',
#                  'precip_aug', 'precip_sep', 'precip_oct', 'precip_nov', 'precip_dec']


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


df = get_county_codes_as_df()
state_dict_df = {}
for state in states:
    state_dict_df[state] = df[(df['state'] == state)]

print(state_dict_df)
# iterate rows while on col (state) val?