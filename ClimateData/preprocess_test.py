from preprocess import *
from config import *
import pytest
import warnings

def test_preprocess():
  config_load()
  create_working_directory()
  process_files(False)

# ensures that each entry in weather.csv has a corresponding county mapping in county_codes.csv
def test_countycodes():
  missing_codes = []

  # read in county code mappings
  county_map = {}
  with open(f'{outputDir}{countyCodesName}', 'r') as f:
    # eat header
    f.readline()

    lines = f.readlines()
    for line in lines:
      line = line.strip()
      values = line.split(',')

      # store county code as key and uid as value
      county_map[values[1]] = values[0]

  # iterate over data set
  with open(f'{outputDir}{weatherFileName}', 'r') as f:
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
        #warnings.warn(f'missing {code}', RuntimeWarning)
        pytest.fail(f'missing county code {code}')

      