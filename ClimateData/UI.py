#!/usr/bin/env python3
import tkinter as tk
import ttkbootstrap as tkboot
from ttkbootstrap import ttk as TTK
from ttkbootstrap import font as tkfont
import psycopg2
import database

# Setup database connection

conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=PASSWORD")
cur = conn.cursor()

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = tk.Frame(self)
        container.grid(row=0, column=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.title('Climate Data')
        self.geometry('1920x1080')
        tkboot.Style('darkly')
    
        self.frames = {}
        for F in (StartPage, graphPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        button1 = TTK.Button(self, text = "Graph", width="15", bootstyle="secondary", command=lambda: controller.show_frame("graphPage"))
        button2 = TTK.Button(self, text = "Map", width="15", bootstyle="secondary", command=lambda: controller.show_frame("mapPage"))
        button1.grid(row=0, column=1, padx=(450,0), pady=(100,500))
        button2.grid(row=0, column=2, padx=(10,0), pady=(100,500))

        # Photo Widget for Start Page
        img = tk.PhotoImage(file='images/cubic_graph.png')
        label = tk.Label(self, image=img)
        label.image = img
        label.grid(row=0, column=0, padx=(20,10), pady=(100,20))


 
class graphPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
       
        frame = tk.Frame(self, width=1920, height=1080)
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
        label.image = img
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

        # Initialize Dropdown Widget
        dropdown = TTK.Combobox(frame_right, font="Helvetica 15")
        dropdown.set('State')
        dropdown['state'] = 'readonly'
        dropdown['values'] = (['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY'])
        dropdown.bind('<<ComboboxSelected>>', self.gen_table)
        dropdown.grid(row=1, column=1, padx=(0, 400), pady=(10, 10))

        button_back = TTK.Button(frame_right, width="15", text="Back to home", bootstyle="secondary", command=lambda: controller.show_frame("StartPage"))
        button_back.grid(row=0, column=1, padx=(0,500), pady=(100, 20))


        #Dropdown Widget for graph selection
        def gen_graph():
            raise ValueError('Method not yet implemented.')

        dropdown_graphs = TTK.Combobox(frame_right, font="Helvetica 15")
        dropdown_graphs.set('Equation')
        dropdown_graphs['state'] = 'readonly'
        dropdown_graphs['values'] = (['Linear', 'Quadratic', 'Cubic', 'n-degree..'])
        dropdown_graphs.bind('<<ComboboxSelected>>', lambda event: self.gen_table(data_table, event))
        dropdown_graphs.grid(row=3, column=1,  padx=(0, 400), pady=(0, 400))

        # Generate Table Rows
        self.gen_table(data_table)

    def gen_table(self, data_table, event=None):
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


if __name__ == "__main__":
    app = App()
    app.mainloop()

