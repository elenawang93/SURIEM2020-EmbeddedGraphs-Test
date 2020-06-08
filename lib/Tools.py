#Levent Batakci
#6/8/2020
#
#This file contains many basic helper and misc. methods.
import networkx as nx
import numpy as np
import random
import math


###
#TREE PROPERTIES
####

#Returns true/false depending on if the input node is a leaf
def is_leaf(T, node, p):
    #Note: p==node indicates that p is the root of some tree
    if(p != node and len(T[node]) == 1):
        return True
    return False

#True if the node is a leaf, based on function values 
def is_leaf_f(T, n):
    c = list(T[n])
    f = f_(T.nodes[n])
    for i in range(0, len(c)):
        if(f_(T.nodes[c[i]]) < f):
            return False
    return True

#Returns a list (names) of a graph's leaves
def get_leaves(M) :
    n = list(M.nodes)
    
    #Find all of the leaves by checking every node
    leaves = []
    for i in range(0, len(n)):
        if(is_leaf_f(M, n[i])):
            leaves.append(n[i])
    
    return leaves


#Returns a list of a graph's nodes (dictionary objects)
#Also adds the nodes' names to the dictionary for easy access
def listify_nodes(G):
    n = list(G.nodes)
    n_list = []
    for i in range(0, len(n)):
        G.nodes[n[i]]['name'] = n[i]
        n_list.append(G.nodes[n[i]])
    return n_list

#Recursively find the parent
def find_p(n_, G):
    n = G.nodes[n_]
    
    parent = n['p_rep']
    if(n['p_rep'] != n_):
        return find_p(parent, G)
    return n_

#Recursively find the child
def find_c(n_, G):
    n = G.nodes[n_]
    child = n['c_rep']
    if(n['c_rep'] != n_):
        return find_c(child, G)
    return n_

#Returns the function value of a node (dictionary)
def f_(node):
    return node['value']

#Computes and sets the lines of ancestry, given a merge tree and a node
def ancestry_line(M, n,ancestry_dict):
    node = M.nodes[n]
    
    #The ancestry line has already been computed
    if(n in ancestry_dict):
        return 
    
    line = []
    
    #If we aren't at the root...
    if(node['p'] != n):
        p = node['p']
        line.append(p) #Add the parent!
        
        ancestry_line(M, p, ancestry_dict) #Get the rest of the line recursively
        list_append(line,ancestry_dict[p])
    #Why did I use recursion here? Well, this guarantees that we will never do any
    #calculation twice. Consequently, we only need to call ancestry_line on all the leaves.
    
    ancestry_dict[n] = line

#Computes the ancestry dictionary, given a merge tree
#Returns a dictionary
def ancestry(M):
    ancestry_dict= {}
    
    leaves = get_leaves(M)
    for i in range(0,len(leaves)):
        ancestry_line(M, leaves[i], ancestry_dict)
    
    return ancestry_dict


###
#END OF TREE PROPERTIES
###


###
#GEOMETRIC METHODS
###

#Computes the height relative to (0,0) by computing the scalar projection
#direction should be a unit vector!!!
def height(pos, angle):
    return pos[0]*math.cos(angle)+pos[1]* math.sin(angle)

#Essentially rotates the graph by performing vector projection
def reorient(pos, angle):

    norm = angle - math.pi / 2
    
    #testing
    #print("direction: " + str(d) + "  Norm: " + str(norm))

    #Calculate the new positions by computing the vector projection
    for p in pos:
        xNew = height(pos[p], norm)
        yNew = height(pos[p], angle)
        pos[p] = (xNew,yNew)


def get_bounds(pos):
    count = len(list(pos))
    
    xArr = np.empty(count)
    yArr = np.empty(count)
    
    i=0
    for key in pos:
        coords = pos[key]
        
        xArr[i]=coords[0]
        yArr[i]=coords[1]
        i+=1
    
    xMax = np.amax(xArr)
    xMin = np.amin(xArr)
    
    yMax = np.amax(yArr)
    yMin = np.amin(yArr)
    
    return [[xMin, xMax], [yMin, yMax]]

def get_bounds_and_radius(pos):
    bounds = get_bounds(pos)
    
    xRange =  bounds[0][1]-bounds[0][0]
    
    yRange = bounds[1][1]-bounds[1][0]
    
    radius = max(xRange, yRange) * 1.03
    return [radius, bounds]
###
#END OF GEOMETRY
###


###
#RANDOM GENERATION
###

#Makes a random tree, doesn't assign positions
def random_tree(n):
    T = nx.Graph() #This is the tree
    
    T.add_nodes_from([1,n]) #Add n nodes to the tree

    #This list stores the nodes that have yet to be added to the tree.
    #To be clear, these are the nodes with no connection to the tree.    
    choices = list(range(2,n+1)) 
    
    #This list stores the nodes that have been added to the tree. By default,
    #the tree 'contains' just node 1
    nodes = [1]
    
    #There are no edges yet.
    edge_count = 0
    
    while edge_count < n-1:
        #Choose a random node n1 in the tree
        i1=random.randint(0,len(nodes)-1)
        n1 = nodes[i1]
        
        #Choose a ranom node n2 NOT in the tree
        i2=random.randint(0,len(choices)-1)
        n2 = choices[i2]
        
        #Add n2 to the tree be connecting it to n1
        T.add_edge(n1,n2)
        edge_count = edge_count + 1 #Account for the new edge
        
        #Move n2 to the right list
        choices.remove(n2)
        nodes.append(n2)
    
    return T #return the tree
###
#END OF RANDOM GENERATION
###


###
#DRAWING TOOLS
###

#Gets the average x position of a node's children
def get_x_pos(T, n, p, pos):
    avg = 0
    c = list(T[n])
    count = 0
    for i in range(0, len(c)):
        if(c[i] != p):
            avg = avg + pos[c[i]][0]
            count = count + 1
    return avg / count
        
#Shifts a node and all its descendants 
def shift(T, n, pos, p, amount):
    pos[n] = (pos[n][0]+amount,pos[n][1])
    c = list(T[n])
    for i in range(0,len(c)):
        if(c[i] != p):
            shift(T, c[i], pos, n, amount)

#Gets the average x position of a node's children, based on a function
def get_x_pos_f(T, n, pos):
    avg = 0
    c = list(T[n])
    count = 0
    f = f_(T.nodes[n])
    for i in range(0, len(c)):
        if(f_(T.nodes[c[i]]) < f):
            avg = avg + pos[c[i]][0]
            count = count + 1
    return avg / count
        
#Shifts a node and all its descendants, based on a function
def shift_f(T, n, pos, amount):
    pos[n] = (pos[n][0]+amount,pos[n][1])
    c = list(T[n])
    f = f_(T.nodes[n])
    for i in range(0,len(c)):
        if(f_(T.nodes[c[i]]) < f):
            shift(T, c[i], pos, amount)
###
#END OF DRAWING TOOLS
###


###
#MISC. METHODS
###

#Adds all the elements in L2 to the end of L1, preserving order
def list_append(L1, L2):
    for i in range(0,len(L2)):
        L1.append(L2[i])

#Performs a BFS search and returns the nodes, parent, and level dictionaries
def BFS(G, r):
    #Level Dictionary.
    #Maps each node to a level. The root is level 0, 
    #and every other node has level < 0. Also, the level
    #of a node is its distance (negated) to the root
    level = {r: 0}
    
    #Parent Dictionary.
    #Maps each node to its parent. The root's parent is itself
    parent = {r:r}
    
    #Children Dictionary.
    #Maps each node to a number denoting the number of children it has.
    children = {}
    
    #List of nodes in order of a BFS
    nodes = []  
    nodes.append(r)
    
    #Create the BFS-tree
    index = 0
    while index < len(nodes):
        #Set the current node to the 'head' of the list
        curr_node = nodes[index]
        
        #Children on the current node. This will actually contain the parent too.
        children = list(G[curr_node])
        
        
        #Add the children, set their levels, and set their parent
        for i in range(0, len(children)):
            if(children[i] not in level): #Ignore the parent 
                level[children[i]] = level[curr_node] - 1
                nodes.append(children[i])
                parent[children[i]] = curr_node
        
        #Move to the next node 
        index = index + 1
    
    #Retrurn the relevant dictionaries and the root    
    return [nodes, parent, level, r]
###
#END OF MISC.
###