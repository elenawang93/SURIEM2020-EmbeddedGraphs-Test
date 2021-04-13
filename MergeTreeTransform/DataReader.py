#Levent Batakci
#6/8/2020
#This program compiles and organizes all our data-reading capabilities
from .lib import txt2nx as txt


from .lib import txt2nx as txt
from .lib import graphml2nx as graphml
from .lib import osm2nx as osm
from .lib import json2nx as json
from .lib import tud2nx as tud
from .lib import sm2nx as sm
from . import ShapeMatcher as ppm


#txt reading
def read_txt(edge_path, vertex_path, main=True):
    g = txt.make_graph(edge_path, vertex_path)
    if(main):
        g[0] = main_component(g[0])
    return g

def read_txt_n(name):
    return txt.make(name)
##

#graphml reading
def read_graphml(path, draw = False, nodeSize = 0, labels = False, main=True):
    g = graphml.read_graphml(path, draw, nodeSize, labels)
    if(main):
        g[0] = main_component(g[0])
    return g
##

#osm reading
def read_osm(path, draw = False, nodeSize = 0, labels = False, main=True):
    g = osm.read_osm(path, draw, nodeSize, labels)
    if(main):
        g[0] = main_component(g[0])
    return g
##

#json
def read_json(path, draw = False, nodeSize = 0, labels = False, main=True):
    g = json.read_json(path, draw, nodeSize, labels)
    if(main):
        g[0] = main_component(g[0])
    return g
##

#img
def read_img(path, draw = False, node_size = 0, labels = False, main=True):
    g = img.read_img(path, draw=draw, nodeSize=node_size, labels=labels)
    if(main):
        g[0] = main_component(g[0])
    return g
##

# large groups of graphs from the TUD data set
def read_tud(path, name, reminder = True):
    g = tud.read_tud(path, name, reminder = reminder)
    return g

# large groups of graphs from the ShapeMaker databases, convert from XML to nx
def read_sm(path):
    g = sm.read_sm(path)
    return g

# large groups of graphs from the ShapeMaker databases, convert directly from binary ppm to nx
def read_ppm(DBname, ppmDir, ppmList = None, SMD = "images/ShapeMatcher"):
    g = ppm.read_ppm(DBname, ppmDir, ppmList, SMD)
    return g

# Returns the largest connected component of a graph as a networkx object
def main_component(G, pos_dict = None, report = True, draw = False):
    largest_cc = max(nx.connected_components(G), key=len)
    mainComponent = G.subgraph(largest_cc).copy()

    if draw == True: # Draw largest component
        if pos_dict == None: # Drawing requires position dictionary
            print("I'll return the main component, but I need position dictionary to draw!")
        else:
            nx.draw(mainComponent, pos = pos_dict, with_labels = False, node_size = 0)

    if report == True: # Tell user what percent of the nodes were preserved
        print("Largest component has ", (len(list(mainComponent.nodes))/len(list(G.nodes)))*100, "% of the nodes")

    return mainComponent
