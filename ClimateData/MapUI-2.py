import pandas
import plotly.express as px
import pandas as pd
import psycopg2
import json
from urllib.request import urlopen
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class MapWindow(QMainWindow):

  def __init__(self, *args, **kwargs):
    super(MapWindow, self).__init__(*args, **kwargs)
    self.window = QWidget()
    self.layout = QVBoxLayout()
    self.navbar = QHBoxLayout()

    self.state_list = QComboBox()
    self.state_list.addItems(["OR","TX","ETC"])
    self.state_list.setMinimumHeight(30)
    self.county_list = QComboBox()
    self.county_list.addItems(["Multnomah","Etc."])
    self.county_list.setMinimumHeight(30)
    self.navbar.addWidget(self.state_list)
    self.navbar.addWidget(self.county_list)

    self.window.setWindowTitle("Climate Data")
    self.browser = QWebEngineView()
    self.browser.setUrl(QUrl('http://127.0.0.1:5500/HTML/map_fig.html'))

    self.layout.addLayout(self.navbar)
    self.layout.addWidget(self.browser)

    self.window.setLayout(self.layout)
    self.window.show()



df = pd.read_csv('data/TX_Data.csv')
f1 = open('data/tx-us-county-codes.txt', 'r')
f = f1.read()
f1.close()
fipslist = f.splitlines()
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
  counties = json.load(response)

# def pull_data():
#   password = 'PASSWORD'
#   conn = psycopg2.connect(f"host=localhost dbname=postgres user=postgres password={password}")
#   cur = conn.cursor()
#   cur.execute("""SELECT * FROM county_codes WHERE state = %s;""", [states_abb[state]])
#   conn.commit()
#   data = cur.fetchall() 
#   return

cli_map = px.choropleth(df, geojson=counties, locations=fipslist, color='Temperature',color_continuous_scale='jet',range_color=(10,130), scope='usa')
cli_map.update_layout(title='Texas')
cli_map.update_geos(fitbounds='locations', visible=False)
cli_map.write_html('HTML/map_fig.html')

app = QApplication([])
window = MapWindow()
app.exec_()