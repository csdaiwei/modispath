# encoding:utf-8

import pdb
import Tkinter as tk
from Tkinter import *
import tkMessageBox
import numpy as np

from PIL import ImageTk, Image
from pyhdf.SD import SD, SDC

import parameters as params


class MainWindow(object):
    """
        non-importable class for ui-building
        run as main program

        On writing new code, make sure your new code is self-consistent
        and make no side efforts on other codes.
        
        Try not add member variables (self.xxx) since less membervar, less maintenance.
        Try not add public functions, it's a class for main.
        Do not modify old code unless they are wrong.

        Feel free to add private functions which won't change the internal state (change value of member variables)
        Add it at right place.

    """

    def __init__(self, master):


        # all member variables are listed below

        # pathes and model
        self.imagefile = 'data/MOD02QKM.A2014005.2110.006.2014218155544_band1.jpg'
        self.probfile = ''
        self.model = None

        self.zoom_factor= 1.0
        self.zoom_level = [0.1, 0.2, 0.5, 0.75, 1.0] 

        # member var for ui
        self.imtk = None
        self.zoom_text = None
        self.canvas = None
        self.mouse_state = tk.IntVar()      # self.mouse_state.get() ==0    # drag mouse to move image
                                            # self.mouse_state.get() ==1    # click to set starting point
                                            # self.mouse_state.get() ==2    # click to set ending point
            
        # now building ui

        # first of all, 3 main frames
        frame_left_top = tk.Frame(master, width=850, height=850)
        frame_left_bottom = tk.Frame(master, width=850, height=60)
        frame_right = tk.Frame(master, width=200, height=910, bg='blue')
        frame_left_top.grid(row=0, column=0, padx=2, pady=2)
        frame_left_bottom.grid(row=1, column=0)
        frame_right.grid(row=0, column=1, rowspan=2, padx=1, pady=2)

        # building frame_left_top
        img = Image.open(self.imagefile)
        self.imtk = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(frame_left_top, width=850, height=850, bg='yellow')
        canvas.create_image(0, 0, image=self.imtk, anchor='nw')

        xbar = tk.Scrollbar(frame_left_top, orient=HORIZONTAL)
        xbar.config(command=canvas.xview)
        xbar.pack(side=BOTTOM, fill=X)

        ybar = tk.Scrollbar(frame_left_top)
        ybar.config(command=canvas.yview)
        ybar.pack(side=RIGHT, fill=Y)

        canvas.config(scrollregion=canvas.bbox(ALL))
        canvas.config(xscrollcommand=xbar.set)
        canvas.config(yscrollcommand=ybar.set)
        self.canvas = canvas
        canvas.pack()


        #building frame_left_bottom
        b0 = tk.Radiobutton(frame_left_bottom, text="默认", variable=self.mouse_state,value=0)
        b1 = tk.Radiobutton(frame_left_bottom, text="设置起点", variable=self.mouse_state ,value=1)
        b2 = tk.Radiobutton(frame_left_bottom, text="设置终点", variable=self.mouse_state ,value=2)
        b3 = tk.Button(frame_left_bottom, text='更换modis图像', command=self.__callback_b3_change_modis)
        b4 = tk.Button(frame_left_bottom, text='显示/隐藏经纬网', command=self.__callback_b4_showhide_geogrids)
        b5 = tk.Button(frame_left_bottom, text='-', width=2, command=self.__callback_b5_zoomout)
        b6 = tk.Button(frame_left_bottom, text='+', width=2, command=self.__callback_b6_zoomin)
        b0.grid(row=0, column=0)
        b1.grid(row=0, column=1)
        b2.grid(row=0, column=2)
        b3.grid(row=0, column=3)
        b4.grid(row=0, column=4)    # a blank label between column 4 and 6
        b5.grid(row=0, column=6)
        b6.grid(row=0, column=8)    # a scale label between column 6 and 8

        blank = tk.Label(frame_left_bottom)
        blank.grid(row=0, column=5, padx=40)

        self.zoom_text = tk.StringVar()
        self.zoom_text.set('%d' % (self.zoom_factor * 100) + '%')
        scale_label = tk.Label(frame_left_bottom, textvariable = self.zoom_text, width=6)
        scale_label.grid(row=0, column=7)



    #######################################
    ### public member functions ###########
    #######################################

    '''no public member func for this class'''

    #######################################
    ### callback functions ################
    #######################################

    # button callbacks (with no event paratemer)

    def __callback_b3_change_modis(self):
        pass

    def __callback_b4_showhide_geogrids(self):
        pass

    def __callback_b5_zoomout(self):
        factor = self.zoom_factor
        index = self.zoom_level.index(factor)
        if index <= 0:
            return
        
        new_factor = self.zoom_level[index - 1]
        self.__rescale(new_factor)


        
    def __callback_b6_zoomin(self):
        factor = self.zoom_factor
        index = self.zoom_level.index(factor)
        if index >= len(self.zoom_level)-1:
            return
        
        new_factor = self.zoom_level[index + 1]
        self.__rescale(new_factor)


    # event callbacks

    def __event_callback(self, event):
        pass

    #######################################
    ### auxiliary functions ###############
    #######################################

    def __rescale(self, new_factor):
        self.zoom_factor = new_factor
        self.zoom_text.set('%d' % (new_factor * 100) + '%')

        img = Image.open(self.imagefile)
        new_size = (int(img.size[0] * new_factor), int(img.size[1] * new_factor))
        self.imtk = ImageTk.PhotoImage(img.resize(new_size, Image.ANTIALIAS))
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')
        self.canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

        
        

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modis')
    root.resizable(width=False, height=False)

    window = MainWindow(root)

    root.mainloop()