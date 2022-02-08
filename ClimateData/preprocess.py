import os
import sys
import csv
import numpy as np
import pandas as pd

datadir = './data/raw/'
outputDir = './data/processed/'
order = ['min', 'avg', 'max', 'precip']
filesToStrip = ['mintmp', 'avgtmp', 'maxtmp', 'precip']
colsPrefix = ['tmp_avg', 'tmp_max', 'tmp_min', 'precip']
months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']


# ensures that each entry in complete.csv has a corresponding county mapping in county_codes.csv
def test_countycodes():
  missing_codes = []

  # read in county code mappings
  county_map = {}
  with open('./data/processed/county_codes.csv', 'r') as f:
    # eat header
    f.readline()

    lines = f.readlines()
    for line in lines:
      line = line.strip()
      values = line.split(',')

      # store county code as key and uid as value
      county_map[values[1]] = values[0]

  # iterate over data set
  with open('./data/processed/complete.csv', 'r') as f:
    # eat header
    f.readline()

    lines = f.readlines()
    for line in lines:
      line = line.strip()
      values = line.split(',')

      # read first 7 characters of id as county code
      code = values[0][:7]
      
      if not code in county_map and not code in missing_codes:
        missing_codes.append(code)
        print(f'missing {code}')

def convert_countycodes():
  state_map = {}
  with open('./data/raw/county-state-codes.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
      line = line.strip()
      values = line.split(' ')
      state_map[values[1]] = values[0]


  # read in postal fips to ncdc fips from county-to-climdivs.txt
  county_map = {}
  with open('./data/raw/county-to-climdivs.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
      line = line.strip()
      if len(line) == 16:
        values = line.split(' ')
        county_map[values[0]] = values[1]

  # converts tab-delimited county codes to comma delimited csv
  with open('./data/raw/us-county-codes.txt', 'r') as f:
    with open('./data/processed/county_codes.csv', 'w') as w:

      # header
      w.write('id INTEGER PRIMARY KEY,county_code INTEGER,county_name VARCHAR(50),state VARCHAR(2),country VARCHAR(3)\n')

      # eat header
      f.readline()

      # iterate lines
      lines = f.readlines()
      id = 1
      for line in lines:
        parts = line.split('\t')

        county_code = parts[0]
        county_state_code = int(county_code[:2])
        state = parts[2].strip()
        name = parts[1]
        skip = False
        #if county_code in county_map:
        #  county_code = county_map[county_code]
        if state in state_map:
          county_code = f'{state_map[state]}{county_code[2:]}'
        else:
          skip = True
          print(f'skipping {line.strip()}')

        if not skip:
          # prepend '01' to code, indicating county is from united states
          # add 'US' value for country column
          w.write(f'{id},01{county_code},{name},{state},US\n')
          id += 1


if __name__ == '__main__':
    icols = [i for i in range(len(months) + 1)]
    dtypes = [str] + [str] * len(months)
    d = pd.DataFrame(np.vstack([icols, dtypes])).to_dict(orient='records')[1]
    dff = pd.DataFrame()


    for filename, prefix, i in zip(filesToStrip, colsPrefix, range(len(colsPrefix))):

        # Build column names
        cols = ['id INTEGER PRIMARY KEY']
        for m in months:
            cols.append(f'{prefix}_{m} FLOAT')

        df = pd.read_csv(f'{datadir}climdiv-{filename}.csv', delimiter=',', header=None, index_col=False, usecols=icols, dtype=d)
        
        # Remove datatype field, since it's the same throughout the entirity of each file
        s = df.iloc[:,0]
        s = s.str[0:5] + s.str[7:]
        df.iloc[:,0] = s

        if i == 0:
            # Add USA Country code
            cc = pd.DataFrame(['01']*len(df), dtype=(str))
            df.iloc[:,0] = cc.iloc[:,0].str[:] + df.iloc[:,0].str[:]

            # Add columns (along with id column this first time)
            df.columns = cols
            dff = pd.DataFrame(df, columns=cols)
        else:
            # Add columns
            df.columns = cols
            # Insure id parity here! 
            for v1, v2 in zip(dff.iloc[:,0], df.iloc[:,0]):
                # Don't compare country code as it hasn't been added to anything but the primary id
                if v1[2:] != v2:
                    raise RuntimeError('Invalid Data Join')

            df = df.iloc[:,1:]
            dff = dff.join(df)

        print(dff)

        # Create individual files
        #df.to_csv(f'{datadir}{filename}.csv', header=False, index=False)

    # WARNING: If you open this file in Excel without specifying the first 
    # column is a string, it will remove all the first zeros in the ID column
    dff.to_csv(f'{outputDir}complete.csv', index=False)
    print('Succesful merge!')

    # process county codes and test the output
    convert_countycodes()
    test_countycodes()
