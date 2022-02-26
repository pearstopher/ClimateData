#!/usr/bin/env python3
import tkinter as tk
import ttkbootstrap as tkboot
from ttkbootstrap import ttk as TTK
from ttkbootstrap import font as tkfont
from ttkbootstrap.constants import *
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

    dropdown_county = None
    data_table = None

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        def on_submit(self):
            raise ValueError('Method not yet implemented.')
       
        frame = tk.Frame(self)
        frame.grid(row=0, sticky="nw")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)            
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        frame_left = tk.Frame(frame)
        frame_right = tk.Frame(frame)
       
        frame_left.grid(row=0, column=0, sticky="nw")
        frame_right.grid(row=0, column=1, sticky="ne") 

        # Initialize Photo widget
        img = tk.PhotoImage(file='images/cubic_graph.png')
        label = tk.Label(frame_left, image=img)
        label.image = img
        label.grid(row=2, column=0, pady=(0, 0), padx=(80, 0))

        #Notebook   
        notebook_label = tk.Label(frame_left, font="12", text="Notebook: ")
        notebook_label.grid(row=1, column=0, padx=(10, 710), pady=(0,10))

        #Date range widgets
        self.begin = tk.StringVar(value="")
        self.end = tk.StringVar(value="")

        ent = tkboot.Entry(frame_right)
        ent.grid(row=4, column=1, padx=(100,0), pady=(0,0))

        ent = tkboot.Entry(frame_right)
        ent.grid(row=5, column=1, padx=(100, 0), pady=(0,0))

        begin_date_label = tk.Label(frame_right, font="10", text="Date range begin: ")
        begin_date_label.grid(row=4, column=1, padx=(0, 250), pady=(0,0))        

        end_date_label = tk.Label(frame_right, font="10", text="Date range end: ")
        end_date_label.grid(row=5, column=1, padx=(0, 265), pady=(0,0))

        sub_btn = tkboot.Button(
            frame_right,
            text="Submit dates",
            command=on_submit,
            bootstyle=SUCCESS,
            width=12,
        )
        sub_btn.grid(row=5, column=1, padx=(430, 0), pady=(0,0))
        sub_btn.focus_set()
        

        # Initialize Table Widget
        self.data_table = TTK.Treeview(frame_right)
        self.data_table['columns'] = ('state', 'county_name', 'county_code', 'country')
        self.data_table.column('#0', width=0, stretch=tk.NO)
        self.data_table.column('state', width=110)
        self.data_table.column('county_name', width=110)
        self.data_table.column('county_code', width=110)
        self.data_table.column('country', width=80)

        self.data_table.heading('#0', text="", anchor=tk.CENTER)
        self.data_table.heading('state', text="State")
        self.data_table.heading('county_name', text="County Name")
        self.data_table.heading('county_code', text="County Code")
        self.data_table.heading('country', text="Country")

        # Initialize State Dropdown Widget
        dropdown_state = TTK.Combobox(frame_right, font="Helvetica 12")
        dropdown_state.set('Select state...')
        dropdown_state['state'] = 'readonly'
        dropdown_state['values'] = (['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY'])
        dropdown_state.bind('<<ComboboxSelected>>', self.gen_counties)
        dropdown_state.grid(row=1, column=1, padx=(0, 190), pady=(20, 20))

        # Initialize Counties Dropdown Widget
        self.dropdown_county = TTK.Combobox(frame_right, font="Helvetica 12")
        self.dropdown_county.set('Select county...')
        self.dropdown_county['state'] = 'readonly'
        self.dropdown_county.bind('<<ComboboxSelected>>', self.gen_table)
        self.dropdown_county.grid(row=1, column=1, padx=(290, 0), pady=(20, 20))

        #Home button
        button_back = TTK.Button(frame_right, width="15", text="Back to home", bootstyle="blue", command=lambda: controller.show_frame("StartPage"))
        button_back.grid(row=0, column=1, padx=(0,250), pady=(100, 10))

        #Add instance to notebook button
        button_notebook_add = TTK.Button(frame_left, width="25", text="Add instance to notebook", bootstyle="blue")
        button_notebook_add.grid(row=0, column=0, padx=(10,580), pady=(50, 20))

        #Dropdown Widget for graph selection
        def gen_graph():
            raise ValueError('Method not yet implemented.')

        dropdown_graphs = TTK.Combobox(frame_right, font="Helvetica 12")
        dropdown_graphs.set('Select equation...')
        dropdown_graphs['state'] = 'readonly'
        dropdown_graphs['values'] = (['Linear', 'Quadratic', 'Cubic', 'n-degree..'])
        #dropdown_graphs.bind('<<ComboboxSelected>>', self.gen_graph)
        dropdown_graphs.grid(row=6, column=1,  padx=(0, 190), pady=(30, 0))

        #Dropdown Widget for data type selection
        data_type_dict = {
            "tmp_avg_jan": "January average temperature",
            "tmp_avg_feb": "February average temperature",
            "tmp_avg_mar": "March average temperature",
            "tmp_avg_apr": "April average temperature",
            "tmp_avg_may": "May average temperature",
            "tmp_avg_jun": "June average temperature",
            "tmp_avg_jul": "July average temperature",
            "tmp_avg_aug": "August average temperature",
            "tmp_avg_sep": "September average temperature",
            "tmp_avg_oct": "October average temperature",
            "tmp_avg_nov": "November average temperature",
            "tmp_avg_dec": "December average temperature",
            "tmp_max_jan": "January maximum temperature",
            "tmp_max_feb": "February maximum temperature",
            "tmp_max_mar": "March maximum temperature",
            "tmp_max_apr": "April maximum temperature",
            "tmp_max_may": "May maximum temperature",
            "tmp_max_jun": "June maximum temperature",
            "tmp_max_jul": "July maximum temperature",
            "tmp_max_aug": "August maximum temperature",
            "tmp_max_sep": "September maximum temperature",
            "tmp_max_oct": "October maximum temperature",
            "tmp_max_nov": "November maximum temperature",
            "tmp_max_dec": "December maximum temperature",
            "tmp_min_jan": "January minimum temperature",
            "tmp_min_feb": "February minimum temperature",
            "tmp_min_mar": "March minimum temperature",
            "tmp_min_apr": "April minimum temperature",
            "tmp_min_may": "May minimum temperature",
            "tmp_min_jun": "June minimum temperature",
            "tmp_min_jul": "July minimum temperature",
            "tmp_min_aug": "August minimum temperature",
            "tmp_min_sep": "September minimum temperature",
            "tmp_min_oct": "October minimum temperature",
            "tmp_min_nov": "November minimum temperature",
            "tmp_min_dec": "December minimum temperature",
            "precip_jan": "January precipitation",
            "precip_feb": "Feburary precipitation",
            "precip_mar": "March precipitation",
            "precip_apr": "April precipitation",
            "precip_may": "May precipitation",
            "precip_jun": "June precipitation",
            "precip_jul": "July precipitation",
            "precip_aug": "August precipitation",
            "precip_sep": "September precipitation",
            "precip_oct": "October precipitation",
            "precip_nov": "November precipitation",
            "precip_dec": "December precipitation",
        }

        def gen_graph():
            raise ValueError('Method not yet implemented.')

        dropdown_graphs = TTK.Combobox(frame_right, font="Helvetica 12")
        dropdown_graphs.set('Select data to plot...')
        dropdown_graphs['state'] = 'readonly'
        dropdown_graphs['values'] = [data_type_dict[x] for x in data_type_dict.keys()]
        #dropdown_graphs.bind('<<ComboboxSelected>>', self.gen_datatype)
        dropdown_graphs.grid(row=7, column=1,  padx=(0, 190), pady=(30, 0))

        # Generate Table Rows
        self.gen_table()

    def gen_counties(self, event=None):
        if event == None:
            county_name = 'no clue what to put here'
        else:
            print("test2")
            county_name = event.widget.get()
        cur.execute("""
        SELECT county_name FROM county_codes WHERE state = %s;
        """,
        [county_name])
        conn.commit()
        data = cur.fetchall()
        print(data)
        self.dropdown_county['values'] = data
        self.dropdown_county.grid(row=1, column=1, padx=(290, 0), pady=(0, 0))

    def gen_table(self, event=None):
        if event == None:
            county_name = ''
            state = ''
        else:
            county_name = event.widget.get()
            state = event.widget.get()
        print('I GOT CALLED')
        #for child in self.data_table.get_children():
            #self.data_table.delete(child)
        cur.execute("""
        SELECT state, county_name, county_code, country FROM county_codes WHERE county_name = %s ;
        """,
        [county_name])
        conn.commit()
        data = cur.fetchall()
        print(data)
        for row in data:
            self.data_table.insert(parent='', index='end', values=row)
        self.data_table.grid(row=2, column=1, pady=(0,40), padx=(250, 235))


if __name__ == "__main__":
    app = App()
    app.mainloop()

