
import pdb

import numpy as np

from  dijkstra_algorithm import dijkstra

from datetime import datetime


class ModisMap(object):
    
    """
        docstring for ModisMap
    """
    
    def __init__(self, prob_mat):

        self.prob_mat = prob_mat        # w*h*3  0:sea, 1:thin ice/cloud, 2:thick ice/cloud
        self.h = prob_mat.shape[0]
        self.w = prob_mat.shape[1]

        
    ############################################################
    #### public methods ########################################
    ############################################################

    # get an path from start to end
    # params:
    #   start   :   (int, int),     matrix subscript of start point
    #   end     :   (int, int)      matrix subscript of destination
    #   ratio   :   float, 0-1      cost = 0.01 + ratio*p(thick/thin ice/cloud) + (1-ratio)*dist
    def getpath(self, start, end, ratio):
        
        assert 0 <= start[0] < self.h
        assert 0 <= start[1] < self.w
        assert 0 <= end[0] < self.h
        assert 0 <= end[1] < self.w
        
        assert isinstance(ratio, float)
        assert 0 <= ratio <= 1

        start_index = self.__matrixcoor2index(start[0], start[1])
        end_index = self.__matrixcoor2index(end[0], end[1])
        

        t1 = datetime.now()

        edges = self.__create_edges(start, end, ratio)

        t2 = datetime.now()

        cost, path = dijkstra(edges, start_index, end_index)
        #cost, path = dijkstra(edges, start, end)

        t3 = datetime.now()

        

        path_points = []
        while path != ():
            node, path = path
            path_points.append(self.__index2matrixcoor(node))
        

        print 'genedges time: %s'%str(t2-t1)
        print 'dijkstra time: %s'%str(t3-t2)
        print 'total time: %s'%str(t3-t1)

        return cost, path_points



    ############################################################
    #### private methods #######################################
    ############################################################    

    #@profile
    def __create_edges(self, start, end, ratio):

        # generate a retangle search area according to start & end
        # todo : make the retangle close to square
        # todo : make sure search area won't out of bounds
        i_search_range = [0, 0]
        j_search_range = [0, 0]
        i_search_range[0] = min(start[0], end[0]) - 10
        i_search_range[1] = max(start[0], end[0]) + 10
        j_search_range[0] = min(start[1], end[1]) - 10
        j_search_range[1] = max(start[1], end[1]) + 10

        offset = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
        dist = [1, 1, 1, 1, 1.414, 1.414, 1.414, 1.414]

        # generate edges in search area 
        # the cost of (p0-p1) is 0.01 + ratio*p(thick/thin ice/cloud | p1) + (1-ratio)*dist
        edges = []
        for index in xrange(0, 8):
            for i in xrange(i_search_range[0], i_search_range[1]):   # right side +1 ?
                for j in xrange(j_search_range[0], j_search_range[1]):
                    i2, j2 = i+offset[index][0], j+offset[index][1]
                    if self.prob_mat[i, j, 0] != np.nan:
                        if self.prob_mat[i2, j2, 0] != np.nan:
                            p0_index = i*self.w + j
                            p1_index = i2*self.w + j2
                            cost = 0.01 + ratio*(1.0 - self.prob_mat[i2, j2, 0]) + (1.0-ratio)*dist[index]
                            edges.append((p0_index, p1_index, cost))
        return edges


    def __matrixcoor2index(self, i, j):
        
        #assert isinstance(i, int) or isinstance(i, long)
        #assert isinstance(j, int) or isinstance(j, long)
        #assert 0 <= i < self.h
        #assert 0 <= j < self.w

        return i*self.w + j

    def __index2matrixcoor(self, index):

        #assert isinstance(index, int) or isinstance(index, long)
        #assert 0 <= index < self.h*self.w
        
        i = index/self.w
        j = index%self.w
        return i, j



if __name__ == '__main__':

    import pickle
    prob_mat = pickle.load(open('data/CURRENT_RASTER_1000.prob', 'rb'))

    model = ModisMap(prob_mat)

    start = (200, 200)
    end = (800, 800)
    ratio = 0.0
    model.getpath(start, end, ratio)