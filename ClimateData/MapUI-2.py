import pandas as pd                             #pip install pandas
import plotly.express as px                     #pip install plotly   
import psycopg2                                 #pip install psycopg2-binary
import json
from urllib.request import urlopen
from PyQt5.QtWidgets import *                   #pip install PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *          #pip install PyQtWebEngine

class MapWindow(QMainWindow):

  def __init__(self, *args, **kwargs):
    
        
    super(MapWindow, self).__init__(*args, **kwargs)
    self.lines = []
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
    self.browser.setUrl(QUrl('http://127.0.0.1:5500/ClimateData/HTML/map_fig.html'))

    self.layout.addWidget(self.browser)
    self.layout.addLayout(self.navbar)
    

    self.window.setLayout(self.layout)
    self.window.show()

  def addLine(self):
      self.addNavbar = QHBoxLayout()
      self.state_list = QComboBox()
      self.state_list.addItems([str(self.layout.count())])
      self.state_list.setMinimumHeight(30)
      self.county_list = QComboBox()
      self.county_list.addItems(["Multnomah","Etc."])
      self.county_list.setMinimumHeight(30)
      self.addNavbar.addWidget(self.state_list)
      self.addNavbar.addWidget(self.county_list)
      self.layout.addLayout(self.addNavbar)
      self.lines.append(self.addNavbar)
 
  def removeLine(self):
      toDelete = self.lines[-1]
      self.deleteLayoutItems(toDelete)
      self.layout.removeItem(toDelete)
      return

  def deleteLayoutItems(self, layout):
    for i in reversed(range(layout.count())): 
      layout.itemAt(i).widget().deleteLater()
      

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