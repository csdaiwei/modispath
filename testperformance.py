
# Dai Wei, csdaiwei@gmail/foxmail.com
#
# This script contains 2 functions, each of them is supposed
# to have a bad time-performance, especially the latter one.
# The purpose i wrote this script is to find a way fixing this problem.


# task 1
# line 10-35 can be moved to a single .py file as a separate module
# try to refine this module by cython
from collections import defaultdict
from heapq import *

def dijkstra(edges, f, t):
    g = defaultdict(list)
    for l,r,c in edges:
        g[l].append((c,r))
    q, seen = [(0,f,())], set()
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)

            if v1 == t:
                return (cost, path)

            for c, v2 in g.get(v1, ()):
                if v2 not in seen:
                    heappush(q, (cost+c, v2, path))

    return (float("inf"), path)



import pdb
import numpy as np
from datetime import datetime


# task 2
# how to improve the time performance of function matrix2graph?
#
# perspectives : 
#   1. basic logic : remove duplicate calculation
#   2. compiler theory & common programing skills
#   3. pythonic, like list comprehension, lambda expression, map/reduce
#   4. thinking & calculating in matrix, do it with careful memory-using
#   5. refine by cython
#   6. ...
#
# tools:
#   cprofiler
#   memory_profiler
#   line_profiler
#   ...
#
def matrix2graph(value_matrix):
    edges = []
    offset = [[0, -1], [-1, 0], [0, 1], [1, 0], [-1, -1], [-1, 1], [1, -1], [1, 1]]
    for index in xrange(0, 8):
        for i in xrange(1, size-1):
            for j in xrange(1, size-1):
                i2, j2 = i+offset[index][0], j+offset[index][1]
                if not np.isnan(value_matrix[i, j]) and not np.isnan(value_matrix[i2, j2]):     # suppose there is np.nan in value_matrix, do not simply ignore it
                    p1_index = coor2index(size, i, j)
                    p2_index = coor2index(size, i2, j2)
                    cost = 0.5*(1.0 - value_matrix[i2, j2]) + 0.5*np.sqrt(offset[index][0]**2 + offset[index][1]**2)     # cost of p1->p2 is 0.5*(1-v[p2])+0.5*dist(p1,p2)
                    edges.append((p2_index, p1_index, cost))
    return edges


def coor2index(size, i, j):
    return i*size + j


#### main ########################################################


# generate a matrix

size = 400
matrix = np.random.rand(size, size)

t1 = datetime.now()

# convert matrix to graph

edges = matrix2graph(matrix)

t2 = datetime.now()

# call dijkstra to get shortest path

cost, path = dijkstra(edges, coor2index(size, 1, 1), coor2index(size, size-2, size-2))        # from (1, 1) to (end-1, end-1) , end is size-1

t3 = datetime.now()

        
print 'genedges time: %s'%str(t2-t1)
print 'dijkstra time: %s'%str(t3-t2)
print 'total time: %s'%str(t3-t1)

