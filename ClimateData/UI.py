#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk as TTK
import psycopg2
import database
# Setup database connection
conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
cur = conn.cursor()

# Initialize Tkinter
root = Tk()
root.title('Climate Data')
root.geometry('1920x1080')

# Initialize Base Frame Widget
frm = TTK.Frame(root, padding=10)
#frm.grid()
frm.pack(fill=BOTH, expand=1)

# Initialize Photo widget
img = PhotoImage(file='images/cubic_graph.png')
label = Label(frm, image=img, justify=LEFT)
#label.grid(row=0, column=0, pady=(0, 100))
label.place(x=50,y=40)

# Initialize Table Widget
data_table = TTK.Treeview(frm)
data_table['columns'] = ('id', 'county_code', 'county_name', 'state', 'country')
data_table.column('#0', width=0, stretch=NO)
data_table.column('id', width=80)
data_table.column('county_code', width=110)
data_table.column('county_name', width=110)
data_table.column('state', width=80)
data_table.column('country', width=80)

data_table.heading('#0', text="", anchor=CENTER)
data_table.heading('id', text="Id")
data_table.heading('county_code', text="County Code")
data_table.heading('county_name', text="County Name")
data_table.heading('state', text="State")
data_table.heading('country', text="Country")

# Function that is called when dropdown value is changed
def gen_table(event=None):
    if event == None:
        state = 'OR'
    else:
        state = event.widget.get()
    print('I GOT CALLED')
    for child in data_table.get_children():
        data_table.delete(child)
    cur.execute("""
    SELECT * FROM county_codes WHERE state = %s;
    """,
    [state])
    conn.commit()
    data = cur.fetchall()
    print(data)
    for row in data:
        data_table.insert(parent='', index='end', values=row)
    #data_table.grid(row=0, column=1, padx=100, pady=(0, 0))
    data_table.place(x=1000,y=100)

# Initialize Dropdown Widget
dropdown = TTK.Combobox(frm, font="Verdana 20 bold")
dropdown['values'] = (['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY'])
dropdown.bind('<<ComboboxSelected>>', gen_table)
dropdown.place(x=1000, y=40)

# Generate Table Rows
gen_table()

# Launch Tkinter
root.mainloop()
