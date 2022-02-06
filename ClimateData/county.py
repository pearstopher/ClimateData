
state_map = {}
with open('./data/county-state-codes.txt', 'r') as f:
  lines = f.readlines()
  for line in lines:
    line = line.strip()
    values = line.split(' ')
    state_map[values[1]] = values[0]


# read in postal fips to ncdc fips from county-to-climdivs.txt
county_map = {}
with open('./data/county-to-climdivs.txt', 'r') as f:
  lines = f.readlines()
  for line in lines:
    line = line.strip()
    if len(line) == 16:
      values = line.split(' ')
      county_map[values[0]] = values[1]

# converts tab-delimited county codes to comma delimited csv
with open('./data/us-county-codes.txt', 'r') as f:
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
      if county_code in county_map:
        county_code = county_map[county_code]
      elif state in state_map:
        county_code = f'{state_map[state]}{county_code[2:]}'
      else:
        skip = True
        print(f'skipping {line.strip()}')

      if not skip:
        # prepend '01' to code, indicating county is from united states
        # add 'US' value for country column
        w.write(f'{id},01{county_code},{name},{state},US\n')
        id += 1
    
