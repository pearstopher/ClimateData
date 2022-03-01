import pandas
import plotly.express as px
import pandas as pd
import psycopg2
import json
from urllib.request import urlopen
from cefpython3 import cefpython as cef

df = pd.read_csv('data/CT_Data.csv')
f1 = open('data/tx-us-county-codes.txt', 'r')
f = f1.read()
f1.close()
fipslist = f.splitlines()
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
  counties = json.load(response)

def pull_data():
  # password = 'PASSWORD'
  # conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
  # cur = conn.cursor()
  # cur.execute("""SELECT * FROM county_codes WHERE state = %s;""", [states_abb[state]])
  # conn.commit()
  # data = cur.fetchall() 
  return

cli_map = px.choropleth(df, geojson=counties, locations=fipslist, color='testVar',color_continuous_scale='rdylgn',range_color=(-10,10), scope='usa')
# cli_map.update_geos(fitbounds='locations', visible=False)
cli_map.update_layout(title='Texas')
cli_map.update_geos(fitbounds='locations', visible=False)
cli_map.write_html('HTML/map_fig.html')

cef.Initialize()
cef.CreateBrowserSync(url="http://127.0.0.1:5500/ClimateData/HTML/map_fig.html" , window_title="Climate Data")
cef.MessageLoop()