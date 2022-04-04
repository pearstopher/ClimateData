from tkinter import HORIZONTAL
import pandas as pd                             #pip install pandas
import plotly.express as px                     #pip install plotly   
import psycopg2                                 #pip install psycopg2-binary
import json
from urllib.request import urlopen
from PyQt5.QtWidgets import *                   #pip install PyQt5
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *          #pip install PyQtWebEngine
import database
import os
import re

datatype_dict = {
    "Maximum temperature" : "tmp_max",
    "Minimum temperature" : "tmp_min",
    "Average temperature" : "tmp_avg",
    "Precipitation"       : "precip"
} 

month_dict = {
    "01" : "jan",
    "02" : "feb",
    "03" : "mar",
    "04" : "apr",
    "05" : "may",
    "06" : "jun",
    "07" : "jul",
    "08" : "aug",
    "09" : "sep",
    "10" : "oct",
    "11" : "nov",
    "12" : "dec"
}


def validate_dates(date):

      #check that date is in correct format (month/year)
      if bool(re.match("\d+\/\d+", date)) == False: 
         return False
      
      [month, year] = date.split('/')

      #check that years are four digits 
      if len(year) != 4:
        return False

      return True

def dateError():
    print("Date Error")

def padWithZero(val):
    if len(val) < 5:
      return "0" + val
    else:
      return val

def updateFIPS(df):
    for idx in range(len(df)):
      df.at[idx, 'fips_code'] = padWithZero(str(df.iat[idx,1]))

# testdf1 = database.get_map_data_for_states(['OR','FL'], 'US', ['tmp_avg'], 'jul', 'jul', 2019, 2019)

class MapWindow(QWindow):

  def __init__(self, pdDF, *args, **kwargs):

    super(MapWindow, self).__init__(*args, **kwargs)
    path = QDir.current().filePath('HTML/map_fig.html')
    self.pdDF = pdDF
    self.lines = []
    self.state_boxes = []
    self.date_boxes = []
    self.curr_month = ''
    self.window = QWidget()
    self.layout = QVBoxLayout()
    self.navbar = QHBoxLayout()
    self.controls = QHBoxLayout()
    self.selection = QHBoxLayout()
    self.echo = QHBoxLayout()

    #Map Controls
    self.yearSlider = QSlider(Qt.Horizontal)
    self.yearSliderBox = QLineEdit()
    self.yearSlider.setMinimum(1895)
    self.yearSlider.setMaximum(2022)
    self.yearSlider.valueChanged.connect(self.yearSlideValChange)
    self.yearSliderBox.returnPressed.connect(self.yearSlideBoxChange)
    self.month_list = QComboBox()
    self.month_list.addItems(['January','February','March','April','May','June','July','August','September','October','November','December'])
    self.month_list.setMinimumWidth(200)

    # self.addButton = QPushButton('+', self.window)
    # self.addButton.setMinimumHeight(30)
    # self.addButton.setMaximumWidth(40)
    # self.addButton.clicked.connect(self.addLine)
    # self.deleteButton = QPushButton('-')
    # self.deleteButton.setMinimumHeight(30)
    # self.deleteButton.setMaximumWidth(40)
    # self.deleteButton.clicked.connect(self.removeLine)

    self.mapItButton = QPushButton('Map it!', self.window)
    self.mapItButton.setMinimumHeight(30)
    self.mapItButton.setMaximumWidth(150)
    self.mapItButton.clicked.connect(self.genMap)
    
    # self.controls.addWidget(self.addButton)
    # self.controls.addWidget(self.deleteButton)

    self.controls.addWidget(self.mapItButton)
    self.controls.addWidget(self.month_list)
    self.controls.addWidget(self.yearSlider)
    self.controls.addWidget(self.yearSliderBox)
    
    #State/County Selection
    self.state_list = QComboBox()
    self.state_list.addItems(['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY'])
    self.county_list = QComboBox()
    self.selection.addWidget(self.state_list)
    self.selection.addWidget(self.county_list)

    #Data table
    self.data_tree = QTreeView()
    self.data_table = QStandardItemModel(0,4)
    self.data_table.setHeaderData(0, Qt.Horizontal, "State")
    self.data_table.setHeaderData(1, Qt.Horizontal, "County Name")
    self.data_table.setHeaderData(2, Qt.Horizontal, "County FIPS")
    self.data_table.setHeaderData(3, Qt.Horizontal, "Country")
    self.data_tree.setModel(self.data_table)
    self.echo.addWidget(self.data_tree)

    #Set title and add widgets and layouts to main window. 
    self.window.setWindowTitle("Climate Data")
    self.browser = QWebEngineView()
    self.openDefaultMap()
    self.layout.addWidget(self.browser)
    self.layout.addLayout(self.controls)
    self.layout.addLayout(self.selection)
    self.layout.addLayout(self.echo)
    self.layout.addLayout(self.navbar)
    self.window.setLayout(self.layout)
    self.window.show()

  #Displays slider value
  def yearSlideBoxChange(self):
    self.yearSlider.setValue(int(self.yearSliderBox.text()))
  #Changes slider value
  def yearSlideValChange(self):
    self.yearSliderBox.setText(str(self.yearSlider.value()))
  def monthSlideBoxChange(self):
    self.monthSlider.setValue(int(self.monthSliderBox.text()))
  #Changes slider value
  def monthSlideValChange(self):
    monthDict = {
    "1" : "January",
    "2" : "February",
    "3" : "March",
    "4" : "April",
    "5" : "May",
    "6" : "June",
    "7" : "July",
    "8" : "August",
    "9" : "September",
    "10" : "October",
    "11" : "November",
    "12" : "December"
    }
    self.monthSliderBox.setText(monthDict[str(self.monthSlider.value())])

  #Generates the map using pandas dataframe
  def genMap(self):
    states = self.getStates()
    dates = self.getDates()
    df = []
    if states:
      dates[0] = dates[0].split('/')
      year = int(dates[0][1])
      self.curr_month = month = month_dict[dates[0][0]]
      print(month)
      print(year)
      df = (database.get_map_data_for_states(states, 'US', ['tmp_avg'], [month], year, year))
      if len(states) > 1:
        for i in range(1, len(states)):
          dates[i] = dates[i].split('/')
          year = dates[i][1]
          month = month_dict[dates[i][0]]
          print(month)
          df.append(database.get_map_data_for_states(states[i], 'US', ['tmp_avg'], [month], year, year))
    print(df)
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
      counties = json.load(response)

    cli_map = px.choropleth(df, geojson=counties, locations='fips_code', color='tmp_avg_'+self.curr_month, color_continuous_scale='jet',range_color=(10,130), scope='usa', hover_name='county_name', hover_data=['state'])
    cli_map.update_layout(title='Climate Data')
    cli_map.update_geos(fitbounds='locations', visible=True)
    cli_map.write_html('HTML/map_fig.html')
    self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath('HTML/map_fig.html')))

  #Used to open blank map of US
  def openDefaultMap(self): 
      self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath('HTML/default_fig.html')))

  #Button control for adding a new line
  def addLine(self):
      self.addNavbar = QHBoxLayout()
      self.state_list = QComboBox()
      self.state_list.addItems(['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY'])
      self.state_list.setMinimumHeight(30)
      self.state_boxes.append(self.state_list)
      self.date = QLineEdit()
      self.date.setMinimumHeight(30)
      self.date.setMaximumWidth(250)
      self.addNavbar.addWidget(self.state_list)
      self.addNavbar.addWidget(self.date)
      self.layout.addLayout(self.addNavbar)
      self.lines.append(self.addNavbar)
      self.date_boxes.append(self.date)
 
 #Button control to remove a line
  def removeLine(self):
      try:
        toDelete = self.lines.pop()
      except:
        return
      self.deleteLayoutItems(toDelete)
      self.layout.removeItem(toDelete)
      self.state_boxes.pop()
      self.date_boxes.pop()
      return

  #Helper function to remove line.
  def deleteLayoutItems(self, layout):
    for i in reversed(range(layout.count())): 
      layout.itemAt(i).widget().clear()

  #Gets a list of states selected for every line
  def getStates(self):
    states = []
    for boxes in self.state_boxes:
      states.append(boxes.currentText())
    return states

  #Gets a list of dates specified on every line.
  def getDates(self):
    dates = []
    for boxes in self.date_boxes:
      if not validate_dates(boxes.text()):
        dateError()
        return
      dates.append(boxes.text())
    return dates
  


if __name__ == "__main__":
  app = QApplication([])
  window = MapWindow('yo')
  app.exec_()