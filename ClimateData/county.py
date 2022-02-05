
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

      # prepend '01' to code, indicating county is from united states
      # add 'US' value for country column
      w.write(f'{id},01{parts[0]},{parts[1]},{parts[2].strip()},US\n')
      id += 1
    
