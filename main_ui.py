# encoding:utf-8

import pdb

import pickle
import tkMessageBox

import numpy as np
import Tkinter as tk
from Tkinter import *

from PIL import ImageTk, Image
from collections import Counter

# todo list 
#   
#   to be developed:
#       callback of entry start/end input      
#       route generatation
#       multi route
#       partial route
#       cost diagrams
#       导出功能
#   
#   ongoing:
#       right click to show mat values    
#
#
#   fix or improve:
#       todo in func MainWindow.__draw_graticule
#       todo in func MainWindow.__find_geocoordinates
#       todo in func MainWindiw.__init_models
#       input check     
#       缩放中心调整
#       路径危险程度颜色绘制



class MainWindow(object):
    
    """
        non-importable class for ui-building
        run as main program

        On writing new code, make sure the new code is self-consistent
        and make less side efforts on other codes.
        
        Try not add member variables (self.xxx) since less membervar, less maintenance.
        Try not add public functions, it's a class for main.
        Do not modify existing code unless it's necessary.

        Feel free to add private functions which won't change the internal state (change value of member variables)
        Add it at right place.

    """

    def __init__(self, master):


        # all member variables are listed below
        # in fact, all these member variables should be private

        # pathes and model
        self.imagefile = None
        self.probfile = None
        self.lonlatfile = None
        self.model = None

        # value matrices
        self.img = None
        self.prob_mat = None
        self.lonlat_mat = None

        self.__init_models('data/CURRENT_RASTER_1000.jpg')

        # member var for ui
        self.imtk = None
        self.zoom_text = None
        self.canvas = None
        self.e1, self.e2, self.e3, self.e4 = None, None, None, None
        self.e5, self.e6, self.e7, self.e8 = None, None, None, None

        # control variables
        self.zoom_factor= 1.0
        self.zoom_level = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5]    # final static
        self.optimize_target = tk.StringVar()   # control var of self.e6 (optionmenu), domain{'', '时间' '油耗', '路程'}
        self.mouse_status = tk.IntVar()         # control var of b0, b1 and b2 (radiobutton group), domain{1, 2, 3}
                                            # self.mouse_status.get() ==0    # drag mouse to move image
                                            # self.mouse_status.get() ==1    # click to set starting point
                                            # self.mouse_status.get() ==2    # click to set ending point

        # canvas tags
        self.tag_graticule = []
        self.tag_start_point = None
        self.tag_end_point = None
        self.tag_query_point = None
        self.tag_rect = None
        self.tag_infotext = None

            
        # now building ui

        # first of all, 3 main frames
        frame_left_top = tk.Frame(master, width=850, height=850)
        frame_left_bottom = tk.Frame(master, width=850, height=50)
        frame_right = tk.Frame(master, width=200, height=900)
        frame_left_top.grid(row=0, column=0, padx=2, pady=2)
        frame_left_bottom.grid(row=1, column=0)
        frame_right.grid(row=0, column=1, rowspan=2, padx=1, pady=2)

        # building frame_left_top
        self.imtk = ImageTk.PhotoImage(self.img)
        canvas = tk.Canvas(frame_left_top, width=850, height=850, bg='grey')
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
        canvas.pack()

        self.canvas = canvas


        # building frame_left_bottom
        b0 = tk.Radiobutton(frame_left_bottom, text="默认", variable=self.mouse_status, value=0)
        b1 = tk.Radiobutton(frame_left_bottom, text="设置起点", variable=self.mouse_status, value=1)
        b2 = tk.Radiobutton(frame_left_bottom, text="设置终点", variable=self.mouse_status, value=2)
        b3 = tk.Button(frame_left_bottom, text='更换modis图像', command=self.__callback_b3_change_modis)
        b4 = tk.Button(frame_left_bottom, text='显示/隐藏经纬网', command=self.__callback_b4_showhide_graticule)
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


        # building frame_right
        l1 = tk.Label(frame_right, text='起点经度')
        l2 = tk.Label(frame_right, text='起点纬度')
        l3 = tk.Label(frame_right, text='终点经度')
        l4 = tk.Label(frame_right, text='终点纬度')
        l5 = tk.Label(frame_right, text='最小间距')
        l6 = tk.Label(frame_right, text='优化目标')
        l1.grid(row=0, column=0, pady=20)
        l2.grid(row=1, column=0, pady=20)
        l3.grid(row=2, column=0, pady=20)
        l4.grid(row=3, column=0, pady=20)
        l5.grid(row=4, column=0, pady=20)
        l6.grid(row=5, column=0, pady=20)
        

        self.e1 = tk.Entry(frame_right, width=10)
        self.e2 = tk.Entry(frame_right, width=10)
        self.e3 = tk.Entry(frame_right, width=10)
        self.e4 = tk.Entry(frame_right, width=10)
        self.e5 = tk.Entry(frame_right, width=10)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        self.e5.grid(row=4, column=1)
        

        option_list = ['时间', '油耗', '路程']
        self.e6 = tk.OptionMenu(frame_right, self.optimize_target, *option_list)
        self.e6.config(width=6)
        self.e6.grid(row=5, column=1)

        b7 = tk.Button(frame_right, command=self.__callback_b7_genpath, text='生成路径')
        b7.grid(row=6, column=0, columnspan=2, pady=20)

        blank = tk.Label(frame_right, height=5)
        blank.grid(row=7)

        l7 = tk.Label(frame_right, text='查询经度')
        l8 = tk.Label(frame_right, text='查询纬度')
        l7.grid(row=8, column=0, pady=20)
        l8.grid(row=9, column=0, pady=20)
        self.e7 = tk.Entry(frame_right, width=10)
        self.e8 = tk.Entry(frame_right, width=10)
        self.e7.grid(row=8, column=1)
        self.e8.grid(row=9, column=1)

        
        b8 = tk.Button(frame_right, command=self.__callback_b8_querycoordinates, text='查询')
        b9 = tk.Button(frame_right, command=self.__callback_b9_reset, text='复位')
        b8.grid(row=10, column=0, columnspan=2, pady=20)
        b9.grid(row=11, column=0, columnspan=2, pady=20)

        # ui widget code ends 

        # event bindings
        canvas.bind("<Button-1>", self.__event_canvas_click)
        canvas.bind("<Button-3>", self.__event_canvas_rightclick)
        canvas.bind("<B1-Motion>", self.__event_canvas_move)

        self.__rescale(0.2)


    ################################################################################
    ### public member functions ####################################################
    ################################################################################

    '''no public member func for this class'''

    ################################################################################
    ### callback functions #########################################################
    ################################################################################

    # button callbacks (with no event paratemer)

    '''
    def __callback(self):
        pass
    '''


    def __callback_b3_change_modis(self):
        
        from tkFileDialog import askopenfilename
        
        options = {}
        options['initialdir'] = 'data'
        options['filetypes'] = [('jpg files', '.jpg')]
        filename = askopenfilename(**options)

        if filename == '':  #cancl
            return  

        imagefile = 'data/' + filename.split('/')[-1]

        if imagefile == self.imagefile: # same file
            return

        # refresh models
        self.__init_models(imagefile)

        # refresh ui
        self.__callback_b9_reset()
        self.__rescale(0.2)


    def __callback_b4_showhide_graticule(self):
        
        if self.tag_graticule != []:
            #hide
            for g in self.tag_graticule:
                self.canvas.delete(g)
            self.tag_graticule = []
        else:
            #show
            self.__draw_graticule()




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


    def __callback_b7_genpath(self):
        pass


    def __callback_b8_querycoordinates(self):
        pass


    def __callback_b9_reset(self):
        
        # clear entries
        for e in [self.e1, self.e2, self.e3, self.e4, self.e5, self.e7, self.e8]:
            e.delete(0, 'end')

        # reset contron variables
        self.optimize_target.set('')
        self.mouse_status.set(0)
        self.tag_graticule = []

        # clear canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')

        # clear canvas tags
        self.tag_graticule = []
        self.tag_start_point = None
        self.tag_end_point = None
        self.tag_query_point = None
        self.tag_rect = None
        self.tag_infotext = None



    # event callbacks

    def __event_canvas_click(self, event):

        canvas = event.widget
        x, y = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))     # x y is canvas coordinates

        if x <= 0 or x >= self.imtk.width() or y <= 0 or y >= self.imtk.height():
            return 

        status = self.mouse_status.get()

        if status == 0:     # normal
            canvas.scan_mark(event.x, event.y)
        
        elif status == 1:   # click to set starting point
            
            i, j = self.__canvascoor2matrixcoor(x, y)
            lon = self.lonlat_mat[i, j][0]
            lat = self.lonlat_mat[i, j][1]

            self.e1.delete(0, 'end')
            self.e1.insert(0, str('%0.2f'%lon))
            self.e2.delete(0, 'end')
            self.e2.insert(0, str('%0.2f'%lat))

            self.__draw_start_point()


        elif status == 2:   # click to set ending point
            i, j = self.__canvascoor2matrixcoor(x, y)
            lon = self.lonlat_mat[i, j][0]
            lat = self.lonlat_mat[i, j][1]

            self.e3.delete(0, 'end')
            self.e3.insert(0, str('%0.2f'%lon))
            self.e4.delete(0, 'end')
            self.e4.insert(0, str('%0.2f'%lat))

            self.__draw_end_point()

        else:
            raise Exception('mouse status error')


    def __event_canvas_rightclick(self, event):
        
        canvas = event.widget
        x, y = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))     # x y is canvas coordinates

        if x <= 0 or x >= self.imtk.width() or y <= 0 or y >= self.imtk.height():
            return 

        if self.tag_query_point != None:
            self.canvas.delete(self.tag_query_point)
            self.canvas.delete(self.tag_rect)
            self.canvas.delete(self.tag_infotext)
            self.tag_query_point = self.tag_rect = self.tag_infotext = None
            return

        i, j = self.__canvascoor2matrixcoor(x, y)

        lon = self.lonlat_mat[i, j][0]
        lat = self.lonlat_mat[i, j][1]
        prob = self.prob_mat[i, j]

        x_offset, y_offset = 200, 60

        if event.x >= int(self.canvas['width']) - x_offset:
            x_offset = -x_offset
        if event.y >= int(self.canvas['height']) - y_offset:
            y_offset = -y_offset

        self.tag_query_point = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='green')
        self.tag_rect = self.canvas.create_rectangle(x, y, x+x_offset, y+y_offset, outline="grey", fill="grey")
        self.tag_infotext = None


    def __event_canvas_move(self, event):

        canvas = event.widget

        if self.mouse_status.get() == 0:     # normal
            canvas.scan_dragto(event.x, event.y, gain=1)




    ################################################################################
    ### auxiliary functions ########################################################
    ################################################################################

    # refresh ui according to certain zoom factor
    def __rescale(self, new_factor):

        assert new_factor in self.zoom_level

        # save scrollbar position before rescaling
        xa, xb = self.canvas.xview()
        ya, yb = self.canvas.yview()

        # do rescaling works
        self.zoom_factor = new_factor
        self.zoom_text.set('%d' % (new_factor * 100) + '%')

        new_size = (int(self.img.size[0] * new_factor), int(self.img.size[1] * new_factor))
        self.imtk = ImageTk.PhotoImage(self.img.resize(new_size))          # self.img is not resized
        self.canvas.create_image(0, 0, image=self.imtk, anchor='nw')
        self.canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

        #todo: draw other things
        self.__draw_start_point()
        self.__draw_end_point()
        self.tag_query_point = self.tag_rect = self.tag_infotext = None
        if self.tag_graticule != []:
            self.__draw_graticule()

        # fix wrong position of scrollbar after rescaling
        xm = (xa + xb)/2
        ym = (ya + yb)/2
        nxlen = float(self.canvas['width']) / new_size[0]
        nylen = float(self.canvas['height']) / new_size[1]
        nxa = (xm - nxlen/2)
        nya = (ym - nylen/2)

        self.canvas.xview_moveto(nxa)
        self.canvas.yview_moveto(nya)



    # load matrix files and init models
    def __init_models(self, imagefile):

        self.imagefile = imagefile
        self.probfile = self.imagefile[0:-4] + '.prob'
        self.lonlatfile = self.imagefile[0:-4] + '.lonlat'

        #todo : file existence

        beta = 5

        fprob = open(self.probfile,'rb')
        flonlat = open(self.lonlatfile, 'rb')

        self.prob_mat = pickle.load(fprob)
        self.lonlat_mat = pickle.load(flonlat)
        
        self.img = Image.open(imagefile)
        self.img = self.img.crop((0, 0, (self.img.width/beta)*beta, (self.img.height/beta)*beta))# divisible by beta

        self.model = None

        assert self.prob_mat.shape[0:2] == self.lonlat_mat.shape[0:2]
        assert self.prob_mat.shape[0] * beta  == self.img.size[1]
        assert self.prob_mat.shape[1] * beta  == self.img.size[0]


    def __canvascoor2matrixcoor(self, x, y):
        
        assert isinstance(x, int) or isinstance(x, long)
        assert isinstance(y, int) or isinstance(y, long)
        assert 0 <= x < self.imtk.width()
        assert 0 <= y < self.imtk.height()

        beta = 5

        i = int((y / self.zoom_factor) / beta)  # int division
        j = int((x / self.zoom_factor) / beta)

        assert 0 <= i < self.prob_mat.shape[0]
        assert 0 <= j < self.prob_mat.shape[1]

        return i, j


    def __matrixcoor2canvascoor(self, i, j):

        assert isinstance(i, int) or isinstance(i, long)
        assert isinstance(j, int) or isinstance(j, long)
        assert 0 <= i < self.prob_mat.shape[0]
        assert 0 <= j < self.prob_mat.shape[1]

        beta = 5

        x = int(j * beta * self.zoom_factor)
        y = int(i * beta * self.zoom_factor)

        #assert 0 <= x < self.imtk.width()
        #assert 0 <= y < self.imtk.height()

        return x, y

    # returns (i, j) that lonlat_mat[i, j] == (longitude, latitude)
    # this func is suspected tp have a precision problem, leave a todo here.
    def __find_geocoordinates(self, longitude, latitude):

        assert isinstance(longitude, float)
        assert isinstance(latitude, float)

        lon_mat = self.lonlat_mat[:, :, 0]
        lat_mat = self.lonlat_mat[:, :, 1]
        ilen, jlen = lat_mat.shape

        vset = set([])
        for i in range(1, ilen-1):      # for each row i, find all j that (lon_mat[i, j] - lon) <= 0.01
            for j in (np.fabs(lon_mat[i, :] - longitude) < 0.01).nonzero()[0].tolist():
                vset.add((i, int(j)))
        
        if len(vset) == 0:
            # not found, raise error
            print 'target lon %s, lat %s'%(longitude, latitude)
            raise ValueError('longitude not found, vset 0')

        vlist = list(vset)
        lat = np.array([lat_mat[v[0], v[1]] for v in vlist])
        t = np.fabs(lat - latitude).argmin()
        diff =  np.fabs(lat[t] - latitude)
        
        if diff > 0.5:          # so that precision of lon is 0.01, but precision of lat is 0.5
            print 'target lon %s, lat %s'%(longitude, latitude)
            raise ValueError('latitude not found')

        i, j = vlist[t]
        return int(i), int(j)


    def __draw_graticule(self):

        # According to new data, the modis image is transformed by zenithal projection.
        # We can assume that longitude is straight line, latitude is circle (this is assured by zenithal projection)
        # and the polar point should be seated in the image (this is not)
        # Otherwise, we can use code in old system to draw graticule which can deal with twisted graticule

        # This function cannot deal with situation that polar is not within the image
        # Todo :
        #   1. To improve accuracy, use canvas coordinates directly (like drawing latitude) to draw longitude
        #   2. Deal with sitution that polar is not within the image

        for g in self.tag_graticule:
            self.canvas.delete(g)   # clear old and draw new
        self.tag_graticule = []

        lon_mat = self.lonlat_mat[:, :, 0]
        lat_mat = self.lonlat_mat[:, :, 1]
        ilen, jlen = lat_mat.shape

        polar = [None, None]  # lat_mat[polar] is 90N or 90S

        width = 2
        fontsize = 11
        if self.zoom_factor <= 0.6:
            width = 1
            fontsize = 10
        if self.zoom_factor <= 0.2:
            width = 1
            fontsize = 9

        # find vertical longitude line 180 or 0
        j_list = []
        for i in range(0, ilen, 10):
            for v in [0, 180]:
                j = int(np.fabs(lon_mat[i, :] - v).argmin())
                diff = np.fabs(lon_mat[i, j] - v)
                if diff < 0.5:
                    j_list.append(int(j))

        if j_list != []: # founded
            target_j = Counter(j_list).most_common(1)[0][0] # mode of j_list
            x1, y1 = self.__matrixcoor2canvascoor(0, target_j)
            x2, y2 = self.__matrixcoor2canvascoor(ilen-1, target_j)
            g = self.canvas.create_line(x1, y1, x2, y2, fill='SeaGreen', width=width) 
            t = self.canvas.create_text(x2-2, y2-1, anchor='se', font=("Purisa",fontsize), fill='SeaGreen', text=str(int(round(lon_mat[ilen-1, target_j]))))
            self.tag_graticule.append(g)
            self.tag_graticule.append(t)

            polar[1] = int(target_j)

        # draw other longitude lines, such as 150(-30), 120(-60) etc
        interv = 15
        for v in range(0+interv, 180, interv):
            
            # draw line v(-180+v)
            # search by column, for every column j find i that lon[i, j] == v (or -180+v)
            # draw a line between (i0, j0) and (in, jn)
            # notice that vertical line cannot be drawn by this way

            i_list, j_list = [], []
            for j in range(0, jlen, 2):
                for t in [v, -180+v]:
                    i = int(np.fabs(lon_mat[:, j] - t).argmin())
                    diff = np.fabs(lon_mat[i, j] - t)
                    if diff < 0.5:
                        i_list.append(i)
                        j_list.append(j)

            if i_list != []:
                x1, y1 = self.__matrixcoor2canvascoor(i_list[0], j_list[0])
                x2, y2 = self.__matrixcoor2canvascoor(i_list[-1], j_list[-1])
                g = self.canvas.create_line(x1, y1, x2, y2, fill='SeaGreen', width=width) 
                t = self.canvas.create_text(x2-2, y2-1, anchor='se', font=("Purisa",fontsize), fill='SeaGreen', text=str(int(round(lon_mat[i_list[-1], j_list[-1]]))))
                self.tag_graticule.append(g)
                self.tag_graticule.append(t)

                if v == 90:
                    polar[0] = int(i_list[0])   # 90 longitude line is totally horizontal

        assert polar[0] != None and polar[1] != None
        assert 0 < polar[0] < ilen          
        assert 0 < polar[1] < jlen
        
        # draw latitude circles
        # notice that all latitude circles center at polar
        # so once found the center and radius, then the circle can be drawn 
        interv = 10
        for v in range(0, 90, interv):
            
            t = v if lat_mat[0, 0] > 0 else -v 

            # find a point (i, j) on the circle that lat_mat[i, j] = t
            i = polar[0]
            j = int(np.fabs(lat_mat[i, :] - t).argmin())    # first, try to find (i, j) that i equals polar[0]
            if np.fabs(lat_mat[i, j] - t) > 0.5:            # if not found, try (i, j) that j equals ploar[1]
                j = polar[1]
                i = int(np.fabs(lat_mat[:, j] - t).argmin())
                if np.fabs(lat_mat[i, j] - t) > 0.5:
                    continue    # also not found , no more work to draw this latitude circle
            
            # from now on, use canvas coordinates instead of matrix coordinates to improve accuracy
            x0, y0 = self.__matrixcoor2canvascoor(polar[0], polar[1])   # canvas coordinates of the center
            x1, y1 = self.__matrixcoor2canvascoor(i, j)                 # canvas coordinates of (i, j)
            radius = ((x1-x0)**2 + (y1-y0)**2)**0.5

            xlen, ylen = self.imtk.width(), self.imtk.height()

            for sign in [1, -1]: # lower half circle and upper half circle
                circle_points = [[]]
                for x in range(max(int(x0-radius), 0), min(int(x0+radius+1), xlen)):
                    y = y0 + sign * (radius**2 - (x-x0)**2)**0.5
                    if 0<= y < ylen:
                        circle_points[-1].append((x, y))
                    else:
                        if circle_points[-1] != []:
                            circle_points.append([])
                        else:
                            continue
            
                for points in circle_points:

                    for i in range(0, len(points)-1):
                        cx, cy = points[i]
                        nx, ny = points[i+1]
                        g = self.canvas.create_line(cx, cy, nx, ny, fill='SeaGreen', width=width) 
                        self.tag_graticule.append(g)
                        # how about text?

        # for reference, 
        # code of drawing longitude lines in a line-fitting way 
        # is preserved here as multi-line comments.

        '''
        # draw longitude lines in line fitting way
        for v in [110]:       # cannot draw longitude 180 line by this way since it is fully vertical
            line_points = []
            for i in range(0, ilen, 10):
                lon = lon_mat[i, :]
                j = int(np.fabs(lon - v).argmin())
                diff = np.fabs(lon[j] - v)
                if j > 0 and j < jlen-1 and diff < 0.1:
                    if lat_mat[i, j] > -81: # do not draw longitude lines within -80
                        line_points.append((i, j))

            if len(line_points) < 5:
                continue

            indice = np.random.randint(0, len(line_points), size=5)
            line_points = [line_points[ind] for ind in indice]
            
            X = [p[0] for p in line_points]
            Y = [p[1] for p in line_points]
            line = np.poly1d(np.polyfit(X, Y, 1))   # line fit

            line_points = []
            for i in range(0, ilen):
                v = line(i)
                j = int(v)
                diff = np.fabs(v - j)
                if j > 0 and j < jlen-1 and diff < 0.1:
                    if lat_mat[i, j] >= -80:
                        line_points.append((i, j))

            for i in range(0, len(line_points)-1):
                cx, cy = self.__matrixcoor2canvascoor(line_points[i][0], line_points[i][1])
                nx, ny = self.__matrixcoor2canvascoor(line_points[i+1][0], line_points[i+1][1])

                g = self.canvas.create_line(cx, cy, nx, ny, fill='yellow', width=width)
                self.tag_graticule.append(g)

        '''


        # Also, code for drawing any twisted graticule (old way) are preserved, too. 

        '''
        # draw latitude lines
        for v in [-80, -70, -60, -50]:
            line_points = []
            for j in range(0, jlen, 10):
                lat = lat_mat[:, j]
                i = int(np.fabs(lat - v).argmin())
                diff = np.fabs(lat[i] - v)
                if i > 0 and i < ilen-1  and diff < 0.1:
                    line_points.append((i, j))

            for i in range(0, len(line_points)-1):
                cx, cy = self.__matrixcoor2canvascoor(line_points[i][0], line_points[i][1])
                nx, ny = self.__matrixcoor2canvascoor(line_points[i+1][0], line_points[i+1][1])

                g = self.canvas.create_line(cx, cy, nx, ny, fill='yellow', width=1.5) 
                self.tag_graticule.append(g)

        # draw longitude lines
        for v in [-160, 180, 160, 140, 120, 100]:
            line_points = []
            for i in range(0, ilen, 10):
                lon = lon_mat[i, :]
                j = int(np.fabs(lon - v).argmin())
                diff = np.fabs(lon[j] - v)
                if j > 0 and j < jlen-1 and diff < 0.1:
                    if lat_mat[i, j] > -81: # do not draw longitude lines within -80
                        line_points.append((i, j))

            for i in range(0, len(line_points)-1):
                cx, cy = self.__matrixcoor2canvascoor(line_points[i][0], line_points[i][1])
                nx, ny = self.__matrixcoor2canvascoor(line_points[i+1][0], line_points[i+1][1])

                g = self.canvas.create_line(cx, cy, nx, ny, fill='yellow', width=1.5)
                self.tag_graticule.append(g)
        '''

        


    def __draw_start_point(self):
        
        if self.tag_start_point != None:
            self.canvas.delete(self.tag_start_point)
            self.tag_start_point = None

        if self.e1.get() == '' or self.e2.get() == '':
            return

        lon = float(self.e1.get())
        lat = float(self.e2.get())

        i, j = self.__find_geocoordinates(lon, lat)
        x, y = self.__matrixcoor2canvascoor(i, j)

        self.tag_start_point = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='red')



    def __draw_end_point(self):

        if self.tag_end_point != None:
            self.canvas.delete(self.tag_end_point)
            self.tag_end_point = None

        if self.e3.get() == '' or self.e4.get() == '':
            return

        lon = float(self.e3.get())
        lat = float(self.e4.get())

        i, j = self.__find_geocoordinates(lon, lat)
        x, y = self.__matrixcoor2canvascoor(i, j)

        self.tag_end_point = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='blue')



if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modis')
    root.resizable(width=False, height=False)

    window = MainWindow(root)

    print dir(window)

    root.mainloop()