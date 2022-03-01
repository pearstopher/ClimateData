import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
import numpy.polynomial.polynomial as poly
import pandas as pd
import mplcursors # TODO find implementation if necessary
from string import ascii_lowercase
import tkinter as tk
from tkinter import *

# Include import statement to get data
matplotlib.use("TkAgg")

csv_path = './data/raw/climdiv-avgtmp.csv'
# Can probably leave headers if importing df is formatted like this
headers = ['Codes', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def get_test_data():
    df = pd.read_csv(csv_path, delimiter=',', nrows=127, header=None)
    df.columns = headers

    print(df.head())

    x_dates_format = []
    x_data = []
    for i in df['Codes']:
        for j in range(1, 13):
            x_dates_format.append(str(i)[-4:] + '-' + str(j))
            x_data.append(int(str(i)[-4:]) + (j - 1) / 12)

    y_data = []
    for i, row in df.head(127).iterrows():
        for j in row[1:]:
            y_data.append(j)

    return [x_data, y_data, x_dates_format]


def get_test_data_raw():
    df = pd.read_csv(csv_path, delimiter=',', nrows=127, header=None)
    df.columns = headers
    return df


class PlottingFrame():
    def __init__(self, master, *args, **kwargs):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.df = get_test_data_raw()
        self.plot_type = args[0]
        self.button = Button(master=window,
                         command=self.plot('scatter_poly', get_test_data_raw(), {'process_type': 'months', 'range': range(0,12), 'degree': 3}),
                         height=2,
                         width=10,
                         text="Plot")
        self.button.pack()
        self.frame = tk.Frame((self.master))

    def plot(self, ptype, df, plot_vars_map):

        x_data, y_data = self.process_data(df, plot_vars_map['process_type'], plot_vars_map['range'])
        if ptype == 'scatter':
            pass
        elif ptype == 'poly':
            pass
        elif ptype == 'scatter_poly':
            self.scatter_poly(x_data, y_data, plot_vars_map['degree'])
        elif ptype == 'us_heatmap':
            pass
        else:
            return 'Invalid plot type!'


    def process_data(self, df, process_type, data_range):
        x_data = []
        y_data = []

        if process_type == 'months':
            for i in self.df.iloc[:,0]:
                for j in data_range:
                    x_data.append(int(str(i)[-4:]) + j / 12)

            for i, row in df.iterrows():
                for j in row[data_range.start+1:data_range.stop+1]:
                    y_data.append(j)
        return x_data, y_data

    def scatter_poly(self, x, y, deg):
        coeffs = poly.polyfit(x, y, deg)
        def fiteq(x, idx=0):
            if idx == deg:
                return coeffs[idx] * x ** (idx)
            else:
                return coeffs[idx] * x ** (idx) + fiteq(x, idx+1)

        x_fit = np.array(x)
        y_fit = fiteq(x_fit)

        fig, ax1 = plt.subplots()
        lines = ax1.plot(x_fit, y_fit, color='r', alpha=0.5, label='Polynomial fit')
        scatter = ax1.scatter(x, y, s=4, color='b', label='Data points')
        ax1.set_title(f'Polynomial fit example deg={deg}')
        ax1.legend()
        plt.subplots_adjust(right=0.8)
        plt.table([['{:.10f}'.format(coeffs[x])[:9]] for x in range(len(coeffs)-1, -1, -1)],
                  rowLabels=[ascii_lowercase[x] for x in range(deg+1)],
                  colLabels=['Poly Coeffs'], loc='right', colWidths = [0.2])

        self.canvas = FigureCanvasTkAgg(fig, master=window) # window is main tkinter window
        self.canvas.get_tk_widget().pack()

        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(self.canvas,
                                       window)
        toolbar.update()
        # placing the toolbar on the Tkinter window
        self.canvas.get_tk_widget().pack()


if __name__ == '__main__':
    # TODO: Add plot color preferences to the input map

    window = Tk()
    window.title('Plotting in Tkinter')
    window.geometry("500x500")
    plotting = PlottingFrame(window, 'scatter_poly')
    window.mainloop()
