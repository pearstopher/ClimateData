import pandas as pd                             #pip install pandas
import plotly.express as px                     #pip install plotly   
import psycopg2                                 #pip install psycopg2-binary
import json
from urllib.request import urlopen
from PyQt5.QtWidgets import *                   #pip install PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *          #pip install PyQtWebEngine
import os

class MapWindow(QMainWindow):

  def __init__(self, *args, **kwargs):
    
        
    super(MapWindow, self).__init__(*args, **kwargs)
    path = QDir.current().filePath('HTML/map_fig.html')
    self.lines = []
    self.window = QWidget()
    self.layout = QVBoxLayout()
    self.navbar = QHBoxLayout()
    self.controls = QHBoxLayout()

    self.addButton = QPushButton('+', self)
    self.addButton.setMinimumHeight(30)
    self.addButton.setMinimumWidth(30)
    self.addButton.clicked.connect(self.addLine)
    self.deleteButton = QPushButton('-')
    self.deleteButton.setMinimumHeight(30)
    self.deleteButton.setMinimumWidth(30)
    self.deleteButton.clicked.connect(self.removeLine)
    self.mapItButton = QPushButton('Map it!', self)
    self.mapItButton.setMinimumHeight(30)
    self.mapItButton.clicked.connect(self.genMap)
    self.controls.addWidget(self.addButton)
    self.controls.addWidget(self.deleteButton)
    self.controls.addWidget(self.mapItButton)
   

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
    self.openMap()
    self.layout.addWidget(self.browser)
    self.layout.addLayout(self.controls)
    self.layout.addLayout(self.navbar)
    

    self.window.setLayout(self.layout)
    self.window.show()

  def genMap(self):
    df = pd.read_csv('data/TX_Data.csv')
    f1 = open('data/tx-us-county-codes.txt', 'r')
    f = f1.read()
    f1.close()
    fipslist = f.splitlines()
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
      counties = json.load(response)

    cli_map = px.choropleth(df, geojson=counties, locations=fipslist, color='Temperature',color_continuous_scale='jet',range_color=(10,130), scope='usa')
    cli_map.update_layout(title='Texas')
    cli_map.update_geos(fitbounds='locations', visible=False)
    cli_map.write_html('HTML/map_fig.html')
    self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath('HTML/map_fig.html')))

  def openMap(self): 
    self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath('HTML/default_fig.html')))

  def addLine(self):
      self.addNavbar = QHBoxLayout()
      self.state_list = QComboBox()
      self.state_list.addItems([" "])
      self.state_list.setMinimumHeight(30)
      self.county_list = QComboBox()
      self.county_list.addItems(["Multnomah","Etc."])
      self.county_list.setMinimumHeight(30)
      self.addNavbar.addWidget(self.state_list)
      self.addNavbar.addWidget(self.county_list)
      self.layout.addLayout(self.addNavbar)
      self.lines.append(self.addNavbar)
 
  def removeLine(self):
      try:
        toDelete = self.lines.pop()
      except:
        return
      self.deleteLayoutItems(toDelete)
      self.layout.removeItem(toDelete)
      return

  def deleteLayoutItems(self, layout):
    for i in reversed(range(layout.count())): 
      layout.itemAt(i).widget().clear()
      
app = QApplication([])
window = MapWindow()
app.exec_()