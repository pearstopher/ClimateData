from cgitb import text
from tkinter import *
from tkinter import ttk
from tkintermapview import TkinterMapView as TKMV
import psycopg2
import database
conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
cur = conn.cursor()

root = Tk()
root.geometry("1500x900")
root.title("Climate Data Map")
buttonFrame = Frame(root)
buttonFrame.pack()
mapFrame = Frame(root)
mapFrame.pack(side=BOTTOM)

# def SelectOR():
#   map_widget.set_address("Multnomah", "Oregon", "United States")
#   map_widget.set_zoom(6)

# def SelectNY():
#   map_widget.set_address("New York", "United")
#   map_widget.set_zoom(10)
    
def SelectState(event = None):
  state = event.widget.get()
  marker1 = map_widget.set_address(state, marker=True)
  map_widget.set_zoom(7)

# ORButton = Button(buttonFrame, text="Oregon", command=SelectOR)
# ORButton.pack(side=LEFT)
# NYButton = Button(buttonFrame, text="New York", command=SelectNY)
# NYButton.pack(side=LEFT)

#Initialize dropdown Widget *Source Adriana Swantz UI Code
dropdown = ttk.Combobox(buttonFrame, font="Verdana 15 bold")
dropdown['state'] = 'readonly'
dropdown['values'] = (['Alaska','Alabama','Arkansas','Arizona','California','Colorado','Connecticut','Delaware','Florida',
'Georgia','Iowa','Idaho','Illinois','Indiana','Kansas','Kentucky','Louisiana','Massachusetts','Maryland','Maine','Michigan',
'Minnesota','Missouri','Mississippi','Montana','North Carolina','Nevada','Nebraska','New Hampshire','New Jersey','New Mexico',
'New York','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah',
'Virgina','Vermont','Washington','Wisconsin','West Virginia','Wyoming'])
dropdown.bind('<<ComboboxSelected>>', SelectState)
dropdown.pack(pady=10)



# #Initialize Data Table Widget *Source Adriana Swantz UI Code
# data_table = ttk.Treeview(buttonFrame)
# data_table['columns'] = ('id', 'county_code', 'county_name', 'state', 'country')
# data_table.column('#0', width=0, stretch=NO)
# data_table.column('id', width=80)
# data_table.column('county_code', width=110)
# data_table.column('county_name', width=110)
# data_table.column('state', width=80)
# data_table.column('country', width=80)

# data_table.heading('#0', text="", anchor=CENTER)
# data_table.heading('id', text="Id")
# data_table.heading('county_code', text="County Code")
# data_table.heading('county_name', text="County Name")
# data_table.heading('state', text="State")
# data_table.heading('country', text="Country")

# data_table.pack()

map_widget = TKMV(root, width=800, height=600, corner_radius=100)
map_widget.place(relx=0.5, rely=0.5, anchor=CENTER)

root.mainloop()