#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk as TTK
import psycopg2
import database
# Setup database connection
conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
cur = conn.cursor()


# Initialize Tkinter
root = tk.Tk()
root.title('Climate Data')
root.geometry('1920x1080')

frame = tk.Frame(root, width=1920, height=1080)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

frame.grid(row=0, sticky="nw")

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)

frame_left = tk.Frame(frame, bg='#152738')
frame_right = tk.Frame(frame, bg='#1c364d')

frame_left.grid(row=0, column=0, sticky="nw")
frame_right.grid(row=0, column=1, sticky="ne")

# Initialize Photo widget
img = tk.PhotoImage(file='images/cubic_graph.png')
label = tk.Label(frame_left, image=img)
label.grid(row=0, column=0, pady=(70, 1000), padx=(80, 250))


# Initialize Table Widget
data_table = TTK.Treeview(frame_right)
data_table['columns'] = ('id', 'county_code', 'county_name', 'state', 'country')
data_table.column('#0', width=0, stretch=tk.NO)
data_table.column('id', width=80)
data_table.column('county_code', width=110)
data_table.column('county_name', width=110)
data_table.column('state', width=80)
data_table.column('country', width=80)

data_table.heading('#0', text="", anchor=tk.CENTER)
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
    data_table.grid(row=2, column=1, pady=(0,40), padx=(10, 185))


# Initialize Dropdown Widget
dropdown = TTK.Combobox(frame_right, font="Verdana 15 bold")
dropdown['state'] = 'readonly'
dropdown['values'] = (['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY'])
dropdown.bind('<<ComboboxSelected>>', gen_table)
dropdown.grid(row=1, column=1, padx=(0, 340), pady=(10, 10))

# Buttons for selecting map or graph functionality
def display_option():
    raise ValueError('Method not yet implemented.')

button_ui = tk.Button(frame_right, text = "Graph", command = display_option, bd='4')
button_ui.grid(row=0, column=1, padx=(0,435), pady=(10, 20))
map_ui = tk.Button(frame_right, text = "Map", command = display_option, bd='4')
map_ui.grid(row=0, column=1, padx=(0,575), pady=(10,20))

#Dropdown Widget for graph selection
def gen_graph():
    raise ValueError('Method not yet implemented.')

dropdown_graphs = TTK.Combobox(frame_right, font="Verdana 15 bold")
dropdown_graphs['state'] = 'readonly'
dropdown_graphs['values'] = (['Linear', 'Quadratic', 'Cubic', 'n-degree..'])
dropdown_graphs.bind('<<ComboboxSelected>>', gen_graph)
dropdown_graphs.grid(row=3, column=1,  padx=(0, 340), pady=(0, 400))


# Generate Table Rows
gen_table()

# Launch Tkinter
root.mainloop()
