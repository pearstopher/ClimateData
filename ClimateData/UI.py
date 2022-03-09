#!/usr/bin/env python3
import tkinter as tk
import ttkbootstrap as tkboot
from ttkbootstrap import ttk as TTK
from ttkbootstrap import font as tkfont
from ttkbootstrap.constants import *
import psycopg2
from database import *
import plotting
import re
from itertools import chain
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

# Dictionaries
degree_dict = {
    "Linear"     : 1,
    "Quadratic"  : 2,
    "Cubic"      : 3
}

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

#This dictionary makes months abbreviations look nicer in the UI
month_abbrev_to_whole = {

    "01" : "January",
    "02" : "February",
    "03" : "March",
    "04" : "April",
    "05" : "May",
    "06" : "June",
    "07" : "July",
    "08" : "August",
    "09" : "September",
    "10" : "October",
    "11" : "November",
    "12" : "December"


}

# Helper Functions --------------------------------------------------

def validate_dates(start, end):

    #check that date is in correct format (month/year)
    if bool(re.match("\d+\/\d+", start)) == False or bool(re.match("\d+\/\d+", end)) == False: 
        return False
   
    [begin_month, begin_year] = start.split('/')
    [end_month, end_year] = end.split('/')

    #check that years are four digits 
    if len(begin_year) != 4 or len(end_year) != 4:
        return False

    #check that first year occurs before second year
    if bool(begin_year < end_year) == False:
        return False

    return True


def validate_degree(degree):
   
    #check that the degree is a number 
    if bool(degree.isnumeric()) == False:
        return False

    return True


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
            frame = F(parent=container, controller=self, master=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
    
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    
class StartPage(tk.Frame):
    def __init__(self, parent, controller, master):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        button1 = TTK.Button(self, text = "Graph", width="15", bootstyle="secondary", command=lambda: controller.show_frame("graphPage"))
        button2 = TTK.Button(self, text = "Map", width="15", bootstyle="secondary", command=lambda: controller.show_frame("mapPage"))
        button1.grid(row=0, column=1, padx=(450,0), pady=(100,500))
        button2.grid(row=0, column=2, padx=(10,0), pady=(100,500))

        # Photo Widget for Start Page
        '''
         # TODO remove picture and add either:
         # Empty canvas
         # Pre-populated canvas
        '''
        img = tk.PhotoImage(file='images/cubic_graph.png')
        label = tk.Label(self, image=img)
        label.image = img
        label.grid(row=0, column=0, padx=(20,10), pady=(100,20))

 
class graphPage(tk.Frame):
    def __init__(self, parent, controller, master):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.begin_date = tkboot.StringVar(value="")
        self.end_date = tkboot.StringVar(value="")
        self.n_degree = tkboot.StringVar(value="")


# FUNCTIONS -----------------------------------------------------------------
        
        def on_specific_search():
            #Forget the date entry widgets that had been there along with the button, these CAN be retrieved though!
            self.begin_date_label.grid_forget()
            self.end_date_label.grid_forget()
            self.begin_date_ent.grid_forget()
            self.end_date_ent.grid_forget()
            self.sub_btn.grid_forget()
            self.dropdown_equations.grid_forget()
            self.dropdown_graphs.grid_forget()
            self.scatter_checkbox.grid_forget()
            
            #Parse the date range just recieved from user, this is needed for generating
            #drop downs with applicable years and months
            [begin_month, begin_year] = self.begin_date.get().split('/')
            [end_month, end_year] = self.end_date.get().split('/')
            begin_month = month_abbrev_to_whole[begin_month]
            end_month = month_abbrev_to_whole[end_month]

            print("Date range to go off of for detailed search is: ", begin_month, begin_year, end_month, end_year)
            
            self.date_range_label = tk.Label(self.frame_right, font="10", text="Chosen date range:")
            self.date_range_label.grid(row=4, column=1, padx=(0, 240), pady=(20,0))

            self.date_range = tkboot.StringVar(value="")
            self.date_range.set(begin_month + " " + begin_year + " to " + end_month + " " +  end_year)
            self.show_date_range = tk.Label(self.frame_right, font="10", textvariable=self.date_range)
            self.show_date_range.grid(row=4, column=1, padx=(220, 0), pady=(20,0))

            """
            self.info_label = tk.Label(self.frame_right, font="10", text="Select specific years and months: ")
            self.info_label.grid(row=5, column=1, padx=(0,130), pady=(10,10))
            """
              
            #Initialize detailed year and month search entries
            self.specific_years = TTK.Combobox(self.frame_right, width=14, font="Helvetica 10")
            self.specific_years.set('Select years')
            self.specific_years['state'] = 'readonly'
            self.specific_years.bind('<<ComboboxSelected>>', gen_months)
            self.specific_years.grid(row=6, column=1, padx=(0, 270), pady=(10, 0))

            self.specific_months = TTK.Combobox(self.frame_right, width=14, font="Helvetica 10")
            self.specific_months.set('Select months')
            self.specific_months['state'] = 'readonly'
            self.specific_months.bind('<<ComboboxSelected>>', gen_specific_date_table)
            self.specific_months.grid(row=6, column=1, padx=(30, 0), pady=(10, 0))
        
            #Table widget for specific dates
            self.date_table = TTK.Treeview(self.frame_right)
            self.date_table['columns'] = ('Year', 'Month')
            self.date_table.column('#0', width=0, stretch=tk.NO)
            self.date_table.column('Year', width=110)
            self.date_table.column('Month', width=110)
            self.date_table.heading('#0', text="", anchor=tk.CENTER)
            self.date_table.heading('Year', text="Year")
            self.date_table.heading('Month', text="Month")
            self.date_table.grid(row=7, column=1, pady=(10,0), padx=(0,170))


        #called when submit button for date entry is used
        def on_submit():
            #user input is invalid, call validate_dates function
            if validate_dates(self.begin_date.get(), self.end_date.get()) == False:    
                tkboot.dialogs.Messagebox.show_error("Invalid date entry. \nEntry rules: \n- Entry must be in form: 'month/year' \n- Years must be in chronological order \n- Years must be four digits \n- Entry example: '06/1993'", title='Invalid date entry')

            else: 
                #user input is valid, parse it into two months and two years
                print("User entered this begin date: " + self.begin_date.get())
                print("User entered this ending date: " + self.end_date.get())
                print("parsing data into months/ years.....")
                [begin_month, begin_year] = self.begin_date.get().split('/')
                [end_month, end_year] = self.end_date.get().split('/')
                print("Begin month in correct format: " + begin_month)
                print("Begin year in correct format: " + begin_year)
                print("End month in correct format: " + end_month)
                print("End year in correct format: " + end_year)
                
        def on_submit_degree():
           
            if validate_degree(self.ent.get()) == False:
                tkboot.dialogs.Messagebox.show_error("Invalid degree entry. \nDegree must be a number.", title='Invalid degree entry')
            else:
                print("Degree is: ")
                print(self.ent.get())

        def on_checkbox():
            return null

        #The data has been entered/ selected by the user. Here is it:
        def on_enter_data():
            #Coefficient button
            
            self.button_coeff = TTK.Button(self.frame_right, width="15", text="View Coefficients", bootstyle="blue")
            self.button_coeff.grid(row=9, column=1, padx=(220,0), pady=(50, 0))

            self.button_coeff = TTK.Button(self.frame_right, width="16", text="Export data to CSV", bootstyle="blue")
            self.button_coeff.grid(row=9, column=1, padx=(537,0), pady=(50, 0)) 
            

            
            [begin_month, begin_year] = self.begin_date.get().split('/')
            [end_month, end_year] = self.end_date.get().split('/')
            begin_month = month_dict[begin_month]
            end_month = month_dict[end_month]
            
            polynomial_degree = degree_dict[self.dropdown_equations.get()] if self.ent == None else int(self.ent.get())
            data_type =  datatype_dict[self.dropdown_graphs.get()]
            # Intermediate Steps
            rows = self.data_table.get_children()
            states = []
            county_codes = []
            countries = []
            temp_dict = {}
            for line in rows:
                values = self.data_table.item(line)['values']

                if values[0] not in states:
                    states.append(values[0])
                county_codes.append(values[2])
                countries.append(values[3])
            
                print("printing states:")
                print(values[0])
                #make counties list of lists:
                if values[0] in temp_dict:
                    temp_dict[values[0]].append(values[1])
                    print("in if")
                    print(temp_dict[values[0]])
                else:
                    print("in else")
                    temp_dict[values[0]] = [values[1]]
                    print(temp_dict[values[0]])
            
            counties = []
            for key in temp_dict.keys():
                counties.append(temp_dict[key])

            monthsIdx = {'jan' : 0, 'feb' : 1, 'mar' : 2, 'apr': 3, 'may': 4, 'jun': 5, 
                         'jul': 6, 'aug': 7, 'sep': 8, 'oct': 9, 'nov': 10, 'dec': 11}

            df_list = get_data_for_counties_dataset(states, counties, 'US', [data_type], begin_month, end_month, int(begin_year), int(end_year))

            # We only need the ID and the data here - Remove everything else
            # TODO: Make the function only return this data
            for i, df in enumerate(df_list):
                df_list[i] = pd.concat([df_list[i].iloc[:, 0], df_list[i].iloc[:, 4:]], axis=1)

            # Flatten the list of counties
            counties = list(chain(*counties))
            fig = plotting.plot('scatter_poly', df_list, {'process_type': 'months', 'begin_month': monthsIdx[begin_month],
                                                          'degree': polynomial_degree, 'plots_per_graph' : len(df_list), 'counties' : counties})
            canvas = FigureCanvasTkAgg(fig, master=master)  
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, pady=(50, 0), padx=(10, 600))

            #print("\nHere is the data that the user entered: ")
            #print("Begin date month: ")
            #print(begin_month)
            #print("Begin date year: ")
            #print(begin_year)
            #print("End date month: ")
            #print(end_month)
            #print("End date year: ")
            #print(end_year)
            #print("Polynomial degree: ")
            #print(polynomial_degree)
            #print("Data type to plot: ")
            #print(data_type)
            #print("Counties: ")
            #print(counties)
            #print("States: ")
            #print(states)
            #print("County codes: ")
            #print(county_codes)
            #print("Countries: ")
            #print(countries)
            
        def gen_equation(event=None):
            if event == None:
                degree = ''
            else:
                if event.widget.get() == "n-degree..":
                    self.ent = tkboot.Entry(self.frame_right, width="6", textvariable=event.widget.get())
                    self.ent.grid(row=6, column=1, padx=(240,0), pady=(30,0))
                    degree_label = tk.Label(self.frame_right, font="10", text="Degree: ")
                    degree_label.grid(row=6, column=1, padx=(100, 0), pady=(30,0))
                    sub_btn = tkboot.Button(
                        self.frame_right,
                        text="Submit degree",
                        command=on_submit_degree,
                        bootstyle="blue",
                        width=12
                    )
                    sub_btn.grid(row=6, column=1, padx=(450, 0), pady=(30,0))
                    sub_btn.focus_set()
                else:
                    self.ent = None
                    degree = event.widget.get()
                    print("Degree of equation is: ")
                    print(degree_dict[degree])

        def gen_datatype_columns(event):
            print("User selected this data type: " + event.widget.get())
            print("parsing data type into correct format.... ")
            
            columns = event.widget.get()
            #Data type 'columns' for database function 'get_data_for_counties_dataset'
            print("Data type in correct format is: " + datatype_dict[columns])

        def gen_counties(event=None):
            if event == None:
                county_name = ''
            else:
                county_name = event.widget.get()
            cur.execute("""
            SELECT county_name FROM county_codes WHERE state = %s;
            """,
            [county_name])
            conn.commit()
            data = cur.fetchall()
            print("Your query returned this data: ")
            data = [ x[0] for x in data ]
            data = ['All Counties'] + data
            print(data)
            self.dropdown_county['values'] = data
            self.dropdown_county.grid(row=1, column=1, padx=(290, 0), pady=(0, 0))

        #Fill the months dropdown menu
        def gen_months(event=None):
            if event == None:
                months = ''
            else:
                months = event.widget.get()
            data = [('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')]
            self.specific_months['values'] = data
            self.specific_months.grid(row=6, column=1, padx=(60, 0), pady=(10, 60))
            

        #Fill the specific dates table
        def gen_specific_date_table(event=None):
            if event == None:
                year = ''
                month = ''
            else:
                month = event.widget.get()
                year = self.specific_years.get()
            print(self.begin_month) 
            data = [year, month]
            for row in data:
                self.date_table.insert(parent='', index='end', values=row)
            self.date_table.grid(row=6, column=1, pady=(0,20), padx=(250, 235))
    

        def gen_table(event=None):
            if event == None:
                county_name = ''
                state = ''
            else:
                county_name = event.widget.get()
                state = self.dropdown_state.get()
            if county_name == 'All Counties': 
                cur.execute("""
                SELECT state, county_name, county_code, country FROM county_codes WHERE state = %s;
                """,
                [state])
            else:
                cur.execute("""
                SELECT state, county_name, county_code, country FROM county_codes WHERE county_name = %s AND state = %s;
                """,
                [county_name, state])
            conn.commit()
            data = cur.fetchall()
            print("Your query returned this data: ")
            print(data)
            for row in data:
                self.data_table.insert(parent='', index='end', values=row)
            self.data_table.grid(row=2, column=1, pady=(0,20), padx=(250, 235))


        

# WIDGETS ----------------------------------------------------------------------------       

        # Frame
        frame = tk.Frame(self)
        frame.grid(row=0, sticky="nw")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)            
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        # Left Frame
        self.frame_left = tk.Frame(frame)
        self.frame_left.grid(row=0, column=0, sticky="nw")

        # Right Frame
        self.frame_right = tk.Frame(frame)
        self.frame_right.grid(row=0, column=1, sticky="ne") 

        # Initialize Photo widget
        #img = tk.PhotoImage(file='images/cubic_graph.png')
        #label = tk.Label(frame_left, image=img)
        #label.image = img
        #label.grid(row=2, column=0, pady=(0, 0), padx=(80, 0))
   
        """ 
        #Initial image before graph appears
        initial_fig = plotting.plot('scatter_poly', df_list, {'process_type': 'months', 'begin_month': monthsIdx[begin_month],
        canvas = FigureCanvasTkAgg(initial_fig, master=master)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, pady=(50, 0), padx=(10, 600))
        """

        #Notebook   
        self.notebook_label = tk.Label(self.frame_left, font="12", text="Notebook: ")
        self.notebook_label.grid(row=1, column=0, padx=(10, 710), pady=(0,10))

        #Date range widgets
        self.begin_date_ent = tkboot.Entry(self.frame_right, textvariable=self.begin_date, width=10)
        self.begin_date_ent.grid(row=4, column=1, padx=(40,0), pady=(0,0))

        self.end_date_ent = tkboot.Entry(self.frame_right, textvariable=self.end_date, width=10)
        self.end_date_ent.grid(row=5, column=1, padx=(40, 0), pady=(0,0))

        self.begin_date_label = tk.Label(self.frame_right, font="10", text="Date range begin: ")
        self.begin_date_label.grid(row=4, column=1, padx=(0, 250), pady=(0,0))        

        self.end_date_label = tk.Label(self.frame_right, font="10", text="Date range end: ")
        self.end_date_label.grid(row=5, column=1, padx=(0, 265), pady=(0,0))

        self.sub_btn = tkboot.Button(
            self.frame_right,
            text="Detailed date search..",
            command=on_specific_search,
            bootstyle="blue",
            width=18
        )
        self.sub_btn.grid(row=5, column=1, padx=(350, 0), pady=(0,0))
        self.sub_btn.focus_set()


        """
        self.sub_btn = tkboot.Button(
            self.frame_right,
            text="Submit dates",
            command=on_submit,
            bootstyle="blue",
            width=12,
        )
        self.sub_btn.grid(row=5, column=1, padx=(450, 0), pady=(0,0))
        self.sub_btn.focus_set()
        """
        

        # Initialize Table Widget
        self.data_table = TTK.Treeview(self.frame_right)
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
        self.dropdown_state = TTK.Combobox(self.frame_right, font="Helvetica 12")
        self.dropdown_state.set('Select state...')
        self.dropdown_state['state'] = 'readonly'
        self.dropdown_state['values'] = (['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','IA','ID','IL','IN',
                                          'KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE',
                                          'NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX',
                                          'UT','VA','VT','WA','WI','WV','WY'])
        self.dropdown_state.bind('<<ComboboxSelected>>', gen_counties)
        self.dropdown_state.grid(row=1, column=1, padx=(0, 190), pady=(20, 20))

        # Initialize Counties Dropdown Widget
        self.dropdown_county = TTK.Combobox(self.frame_right, font="Helvetica 12")
        self.dropdown_county.set('Select county...')
        self.dropdown_county['state'] = 'readonly'
        self.dropdown_county.bind('<<ComboboxSelected>>', gen_table)
        self.dropdown_county.grid(row=1, column=1, padx=(290, 0), pady=(20, 20))

        #Home button
        self.button_back = TTK.Button(self.frame_right, width="15", text="Back to home", bootstyle="blue", command=lambda: controller.show_frame("StartPage"))
        self.button_back.grid(row=0, column=1, padx=(0,250), pady=(100, 10))

        #Add instance to notebook button
        self.button_notebook_add = TTK.Button(self.frame_left, width="25", text="Add instance to notebook", bootstyle="blue")
        self.button_notebook_add.grid(row=0, column=0, padx=(10,580), pady=(50, 20))

        #Dropdown Widget for equation selection
        self.dropdown_equations = TTK.Combobox(self.frame_right, font="Helvetica 12")
        self.dropdown_equations.set('Select equation...')
        self.dropdown_equations['state'] = 'readonly'
        self.dropdown_equations['values'] = ['Linear', 'Quadratic', 'Cubic', 'Derivative', 'n-degree..']
        self.dropdown_equations.bind('<<ComboboxSelected>>', gen_equation)
        self.dropdown_equations.grid(row=6, column=1,  padx=(0, 190), pady=(30, 0))

        #TODO: add functionality to this checkbox
        #Scatter plot option checkbox
        self.scatter_checkbox = tkboot.Checkbutton(self.frame_right, text="Enable scatter plotting", command=on_checkbox)
        self.scatter_checkbox.grid(row=7, column=1, padx=(0, 230), pady=(10,0))

        #Dropdown for datatype selection
        self.dropdown_graphs = TTK.Combobox(self.frame_right, font="Helvetica 12")
        self.dropdown_graphs.set('Select data type...')
        self.dropdown_graphs['state'] = 'readonly'
        self.dropdown_graphs['values'] = ["Minimum temperature", "Maximum temperature", "Average temperature", "Precipitation"]
        self.dropdown_graphs.bind('<<ComboboxSelected>>', gen_datatype_columns)
        self.dropdown_graphs.grid(row=8, column=1,  padx=(0, 190), pady=(40, 0))


        #Button for submitting all that the user has entered
        self.data_submit = tkboot.Button(
            self.frame_right, 
            command=on_enter_data,
            width="25", 
            text="Graph it!", 
            bootstyle=DEFAULT
        )
        self.data_submit.grid(row=9, column=1, padx=(0,173), pady=(50,0))
        self.data_submit.focus_set()

        # Generate Table Rows
        gen_table()

if __name__ == "__main__":
    app = App()
    app.mainloop()

