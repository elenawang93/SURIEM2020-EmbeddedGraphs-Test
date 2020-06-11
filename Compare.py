#Levent Batakci
#6/9/2020
#
#This program is concerned witht he comparison of merge trees
import networkx as nx
from lib.Tools import f_, get_leaves, list_append
import math

#MEMOIZATION VARIABLES
global D
D = {}
global memo
memo = {}
global tag

#The associated cost of matching a pair of vertices
#from two rooted representations of branchings
def match_cost(mu,su , mv,sv):
    #m represents the minima
    #s represents the saddle
    return max(math.abs(f_(mu)-f_(mv)), math.abs(f_(su)-f_(sv)))

#The associated cost of removing a vertex 
#from a rooted representation of a branching
def remove_cost(A, u,v):
    return math.abs(f_(A.nodes[u])-f_(A.nodes[v]))/2

#Gets all of the child subtrees of a given root branch
def get_child_subtrees(root, minima, T):
    last = minima
    p = T.nodes[minima]['p']
     
    subtrees = []
    while(True):
        neighbors = T[p]
        
        #Add all the subtrees with child saddle p
        for n in neighbors:
            #Check that n is a child and not an ancestor of minima
            if (n != last and f_(n) < f_(p)):
                stree = sub_special(T, n)
                subtrees.append(stree)
        
        #We've traced back to the root
        if(p == root):
            return subtrees
        
        last = p #Update the last variable
        p = T.nodes[p]['p'] #Move to the next ancestor

#Gets a list including n and all of its descendants, recursively
def descendants(G, n):
    global tag
    
    neighbors = G[n]
    
    d = [n]
    for nei in neighbors:
        if(f_(G.nodes[nei]) < f_(G.nodes[n])):
            #Check if already computed
            if((tag + str(n)) not in D):
                D[tag + str(n)] = descendants(G, nei, tag)
            list_append(d, D[tag + str(n)])
           
    return d

#Returns the special subgraph identified by the almost-root
#The almost-root is first node in the graph. 
def sub_special(G, n):
    nodes = []
    nodes.append(G.nodes[n]['p'])
    list_append(nodes, descendants(G, n))

    #Induce the subgraph and return it
    return nx.Graph.subgraph(G, nodes)

#Creates a bipartite graph to represent the connections between two
#sets of child subtrees
def create_bip(list_A, list_B):
    bip = nx.Graph()
    
    #Add all the nodes to the two bipartitions
    #Reliant on the fact that the subtrees were generated by IsEpsSimilar
    for a in list_A:
        bip.add_node(a)       
    for b in sub_B:
        bip.add_node(b)
        
    return bip

#returns a list of ID nodenames
def node_list(subtrees):
    x = []
    for s in subtrees:
        x.append(list(s.nodes)[1])

    return x

#Computes whether two subtrees a and b are matchable. Calls IsEpsSimilar
#    in the case that the computation hasn't yet been computed.
def compute_matchability(a, b, e, memo):
    na = list(a.nodes)
    nb = list(b.nodes)

    #These indices always pull the ID and roots because of how the subtrees are
    #constructed in a previous method. Generally, this will NOT work on subtrees not
    #computed through IsEpsSimilar!!
    root_a = na[0]    
    id_a = na[1]
    root_b= nb[0]
    id_b = nb[1]
    
    #Check if subtree 'a' has an entry corresponding to it in memo
    #Note: because of the input order, we only ever need entries in the
    #      in the order (a,b)
    if(id_a not in memo or id_b not in memo[id_a]): #Result not computed yet
        if(id_a not in memo):
            memo[id_a] = {}
        
        memo[id_a] = IsEpsSimilar(a, b, e, [root_a, root_b], memo)
    
    #Return the result (True or False)
    return memo[id_a][id_b]

#Compute all the removal costs at and below a root
#Return the resulting cost dictionary
def compute_costs(A, root, e, costs={}):
        
    if(root in costs):
        return costs
    
    #Base removal cost
    c = remove_cost(root, A.nodes[root]['p'])
    
    #Account for the necessary removal of descendants
    #Use memoization to speed things up
    neighbors = A[root]
    for nei in neighbors:
        #If nei is a child but its cost hasn't been computed...
        if(f_(A.nodes[nei])):
            if(nei not in costs):
                costs[nei] = compute_costs(A, nei, e, costs)[nei]
            c += costs[nei]
    
    costs[root] = c
    return costs

#Add all the ghosts to the bipartite graph
def who_you_gonna_call(subtrees_A, subtrees_B, costs_A, costs_B, bip, e):
    for a in subtrees_A:
        id_a = list(a.nodes)[1]
        #Could be removed..
        if(costs_A[id_a] <= e):
            bip.add_node("GHOST " + str(id_a))
            bip.add_edge(id_a, "GHOST " + str(id_a))
    for b in subtrees_B:
        id_b = list(b.nodes)[1]
        #Could be removed..
        if(costs_B[id_b] <= e):
            bip.add_node("GHOST " + str(id_b))
            bip.add_edge(id_b, "GHOST " + str(id_b))

def has_ghost(A, a):
    nodes = list(A.nodes)
    
    return ("GHOST " + str(a)) in nodes

def is_ghost(a):
    return (isinstance(a, str) and len(a) >= 5 and a[0:5] == "GHOST")

#Check if all nodes in a set are ghosts
def good_match(A):
    nodes = list(A.nodes)
    print (nodes)
    
    for a in nodes:
        if not is_ghost(a) and len(A[a]) == 0:
            return False
        
    return True

#Returns a subgraph induced by removign certain nodes
def subgraph_without(G, exclude):
    nodes = list(G.nodes)
    
    for ex in exclude:
        nodes.remove(ex)
        
    return G.subgraph(nodes)
    

#determines whether a perfect matching exists in the context of ghost vertices
def has_perfect_matching(bip, part_A, part_B, results={}):
    
    #Parts A and B are lists of non-ghost nodenames
    #ID is used to identify a result
    ID = str(part_A)+"SPLIT"+str(part_B)

    #Check if already computed
    if(ID in results):
        return results[ID]
    
    #BASE CASE, ONE SET IS EMPTY
    #In this case, check that the non-empty set only contains ghosts
    #and deletable nodes
    if(len(part_A) == 0):
        results[ID] = good_match(bip)
        return results[ID]
    if(len(part_B) == 0):
        results[ID] = good_match(bip)
        return results[ID]
    
    #NONEMPTY SET, resort to recursion
    #iterate over all possible matches for the first vert in part_A
    #and recursively determine if there's a possible perfect matching
    a = part_A[0]
    
    #Iterate over the possibilities
    neighbors = list(bip[a])
    print(neighbors)
    for nei in neighbors:
        #Delete the chosen nodes from the list and graph.
        b = subgraph_without(bip, [a, nei])
        
        new_A = part_A.copy()
        new_A.remove(a)
        
        new_B = part_B.copy()
        if(nei in new_B):
            new_B.remove(nei)
            
        
        #Recursively solve the subproblem
        if(has_perfect_matching(b, new_A, new_B, results)):
            results[ID] = True
            return results[ID]
        
    results[ID] = False
    return results[ID]
           
#S and M are two trees to compare
#e is the cost maximum
#roots is an array containing the roots of A and B
#The function returns whether or no the two merge trees are matchable within e
def IsEpsSimilar(A, B, e, roots, memo):

    #Find the root - the highest vertex - of each tree
    root_A = roots[0]
    root_B = roots[1]

    #Compute all costs for ghost-vertex marking
    costs_A = compute_costs(A, root_A, e)
    costs_B = compute_costs(B, root_B, e)
    
    #Get the minima of the two treees.
    #These are crucial to the construction of branch decompositions
    minima_A = get_leaves(A)
    minima_B = get_leaves(B)
    
    #Next, Iterate over all root-branch posibilities for each graph.
    #At each step, we will check if pairing the two root-branches is feasible.
    #If it is feasible, we will iterate over all child subtree pairings, and
    #    we will recursively check for epsilon similarity. We will construct a
    #    bipartite graph with vertices representing the child subtrees. In the
    #    case that a pairing is matchable, an edge will be drawn between the
    #    corresponding vertices in the bipartite representation
    for mA in minima_A:
        for mB in minima_B:
            
            #At this point, a root-branch pairing will be specified.
            #Check if the initial cost of matching this pairing is prohibitive.
            #If it isn't check if the rest of the graph is matchable by considering
            #   all of the child subtrees.
            if(match_cost(mA, root_A, mB, root_B) < e):
                
                #Get a list of all the child subtrees of each root-branch
                subtrees_A = get_child_subtrees(root_A, mA, A)
                subtrees_B = get_child_subtrees(root_B, mB, B)
                
                #Create a bipartite graph representating the matchability of
                #    subtree pairings between the two lists above. Also, save
                #    all of the nodes in lists.
                list_A = node_list(subtrees_A)
                list_B = node_list(subtrees_B)
                bip = create_bip(list_A, list_B)
                
                #Iterate over all child-subtree pairing and compute matchability.
                #Use memoization to use the results of previous computations.
                #Also, fill in the bipartite edges where applicable
                for a in subtrees_A:
                    for b in subtrees_B:
                        if(compute_matchability(a, b, e, memo)):
                            bip.add_edge(list(a.nodes)[1], list(b.nodes)[1])
                
                #At this point, we should have a bipartite graph that encodes the
                #matchability of each child-subtree pairing at the current level.
                #
                #However, we need to account for the posibility of deletion!
                #To do this, we will iterate over all the current vertices in the 
                #bip. graph and mark ghosts by checking their removal cost.
                who_you_gonna_call(subtrees_A, subtrees_B, costs_A, costs_B, bip, e)
                
                #NOW, everything should be set up properly to check for a perfect
                #     matching.
                if(has_perfect_matching(bip, list_A, list_B)):
                    return True
    
    #No matching was found!
    return False
        
                
                
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    