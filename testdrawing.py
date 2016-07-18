# encoding:utf-8

import pdb

import pickle
import numpy as np
import Tkinter as tk

from PIL import ImageTk, Image
from collections import Counter     # to get mode of a list


# task : rewrite func __draw_graticule
# note that do not modify any code outside this function



class MainWindow(object):
    

    def __init__(self, master):


        # pathes and model
        self.imagefile = None

        # value matrices
        self.img = None
        self.lonlat_mat = None

        self.__init_models('data/CURRENT_RASTER_1000.jpg')

        # member var for ui
        self.imtk = None
        self.zoom_text = None
        self.canvas = None

        # control variables
        self.zoom_factor= 1.0
        self.zoom_level = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5]    # final static

        # canvas item tags
        self.tag_graticule = []

            
        # now building ui
        # firstly, determining canvas window size by the system screensize

        basic_size = (master.winfo_screenheight() / 100) * 100 - 150
        basic_size = min(850, max(600, basic_size))     # 600 650 750 850

        # then, 2 main frames
        frame_left_top = tk.Frame(master, width=basic_size, height=basic_size)
        frame_left_bottom = tk.Frame(master, width=basic_size, height=50)
        frame_left_top.grid(row=0, column=0, padx=2, pady=2)
        frame_left_bottom.grid(row=1, column=0)

        # building frame_left_top
        self.imtk = ImageTk.PhotoImage(self.img)
        canvas = tk.Canvas(frame_left_top, width=basic_size, height=basic_size, bg='grey')
        canvas.create_image(0, 0, image=self.imtk, anchor='nw')

        xbar = tk.Scrollbar(frame_left_top, orient=tk.HORIZONTAL)
        xbar.config(command=canvas.xview)
        xbar.pack(side=tk.BOTTOM, fill=tk.X)

        ybar = tk.Scrollbar(frame_left_top)
        ybar.config(command=canvas.yview)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
        canvas.config(xscrollcommand=xbar.set)
        canvas.config(yscrollcommand=ybar.set)
        canvas.pack()

        self.canvas = canvas


        # building frame_left_bottom
       
        b4 = tk.Button(frame_left_bottom, text='显示/隐藏经纬网', command=self.__callback_b4_showhide_graticule)
        b5 = tk.Button(frame_left_bottom, text='-', width=2, command=self.__callback_b5_zoomout)
        b6 = tk.Button(frame_left_bottom, text='+', width=2, command=self.__callback_b6_zoomin)
      
        b4.grid(row=0, column=4)    # a blank label between column 4 and 6
        b5.grid(row=0, column=6)
        b6.grid(row=0, column=8)    # a scale label between column 6 and 8

        blank = tk.Label(frame_left_bottom)
        blank.grid(row=0, column=5, padx=40)


        self.zoom_text = tk.StringVar()
        self.zoom_text.set('%d' % (self.zoom_factor * 100) + '%')
        scale_label = tk.Label(frame_left_bottom, textvariable = self.zoom_text, width=6)
        scale_label.grid(row=0, column=7)



        # ui widget code ends 

        # event bindings
        canvas.bind("<Button-1>", self.__event_canvas_click)
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



    # event callbacks

    def __event_canvas_click(self, event):

        canvas = event.widget
        canvas.scan_mark(event.x, event.y)
        


    def __event_canvas_move(self, event):

        canvas = event.widget
        canvas.scan_dragto(event.x, event.y, gain=1)




    ################################################################################
    ### auxiliary functions ########################################################
    ################################################################################


    ### model related ############################################################

    # load matrix files and init models
    def __init_models(self, imagefile):

        self.imagefile = imagefile
        lonlatfile = self.imagefile[0:-4] + '.lonlat'

        beta = 5
        self.lonlat_mat = pickle.load(open(lonlatfile, 'rb'))
        
        self.img = Image.open(imagefile)
        self.img = self.img.crop((0, 0, (self.img.width/beta)*beta, (self.img.height/beta)*beta))# divisible by beta

        assert self.lonlat_mat.shape[0] * beta  == self.img.size[1]
        assert self.lonlat_mat.shape[1] * beta  == self.img.size[0]



    ### drawing related ############################################################

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

        self.canvas.update_idletasks()
        from time import sleep
        sleep(1)

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

        self.canvas.update_idletasks()
        sleep(1)
        
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


            # the target latitude line is a circle 
            # the center is (x0, y0), radius is known
            # by circle formula, we calculate points on the circle and draw it

            xlen, ylen = self.imtk.width(), self.imtk.height()

            for sign in [1, -1]: # lower half circle and upper half circle
                circle_points = [[]]
                for x in range(max(int(x0-radius), 0), min(int(x0+radius+1), xlen)):    #range function creates a left-close-right-open interval [,) , thus +1 on right side
                    y = y0 + sign * (radius**2 - (x-x0)**2)**0.5    # circle formula
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


        # Code for drawing any twisted graticule (old way) are preserved below, too. 

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



    ### tools ######################################################################

    def __canvascoor2matrixcoor(self, x, y):
        
        assert isinstance(x, int) or isinstance(x, long)
        assert isinstance(y, int) or isinstance(y, long)
        assert 0 <= x < self.imtk.width()
        assert 0 <= y < self.imtk.height()

        beta = 5

        i = int((y / self.zoom_factor) / beta)  # int division
        j = int((x / self.zoom_factor) / beta)

        assert 0 <= i < self.lonlat_mat.shape[0]
        assert 0 <= j < self.lonlat_mat.shape[1]

        return i, j


    def __matrixcoor2canvascoor(self, i, j):

        assert isinstance(i, int) or isinstance(i, long)
        assert isinstance(j, int) or isinstance(j, long)
        assert 0 <= i < self.lonlat_mat.shape[0]
        assert 0 <= j < self.lonlat_mat.shape[1]

        beta = 5

        x = int(j * beta * self.zoom_factor)
        y = int(i * beta * self.zoom_factor)

        #assert 0 <= x < self.imtk.width()
        #assert 0 <= y < self.imtk.height()

        return x, y


####################################################################################
### end of class MainWindow ########################################################
####################################################################################


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modis')
    root.resizable(width=False, height=False)

    window = MainWindow(root)
    root.mainloop()