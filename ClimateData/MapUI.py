from cgitb import text
from tkinter import *
from tkintermapview import TkinterMapView as TKMV

root = Tk()
root.geometry("1500x900")
root.title("Climate Data Map")
buttonFrame = Frame(root)
buttonFrame.pack()
mapFrame = Frame(root)
mapFrame.pack(side=BOTTOM)

def SelectOR():
  map_widget.set_address("Oregon", "United States")
  map_widget.set_zoom(6)

def SelectNY():
  map_widget.set_address("New York", "United")
  map_widget.set_zoom(6)
    

ORButton = Button(buttonFrame, text="Oregon", command=SelectOR)
ORButton.pack(side=LEFT)
NYButton = Button(buttonFrame, text="New York", command=SelectNY)
NYButton.pack(side=LEFT)

map_widget = TKMV(root, width=800, height=600, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5, anchor=CENTER)

root.mainloop()