from pulp import * 
import numpy as np 
import sys 
#Basic set up for graphs
#https://manas.tech/blog/2010/09/16/modelling-graph-coloring-with-integer-linear-programming/
class Graph(): 
    def __init__(self):
        self.num_nodes = 0 
        self.num_edges = 0 
        self._nodes = {}  
        self._edges = {}
    def add_node(self,node): 
        #Stores mapping of name --> node lookup 
        self._nodes[node.name] = node  
        #Indexed by string
        self._edges[node] = [] 
    def check_node(self,node1, node2): 
        if node1 not in self._edges or node2 not in self._edges: 
            return False 
        return True 
    def add_edge(self,node1,node2):
        if self.check_node(node1,node2): 
            self._edges[node1].append(node2)
            self._edges[node2].append(node1) 
    def remove_edge(self,node1,node2): 
        if self.check_node(node1,node2): 
            self._edges[node1].remove(node2)
            self._edges[node2].remove(node1) 
    def print(self): 

        print([k for k in self._nodes.keys()]) 
        for k,e in self._edges.items(): 
            print("Node: " + str(k.name))
            print([n.name for n in e])  
class Node():
    def __init__(self, name="", val=0): 
        self.name = name 
        self.val = val
    # def __eq__(self,other): 
    #     return self.name == other.name 
    # def __hash__(self): 
    #     return hash(self.name) 
#Process all Nodes and Edges out of a txt file
g = Graph() 
node_data = open("nodes.txt","r") 
edge_data = open("edges.txt","r") 
for n in node_data.readlines(): 
    dat = n.strip().split(",") 
    new_node = Node(dat[0][1:],int(dat[1][:-1])) 
    g.add_node(new_node) 
for e in edge_data.readlines(): 
    dat = e.strip().split(",") 
    node1 = g._nodes[dat[0][1:]]
    node2 = g._nodes[dat[1][:-1]] 
    g.add_edge(node1, node2)
# g.print() 


#Problem 1: Solve the basic binary formulation of the graph coloring problem 
def solve_graph(num_colors): 
    colors = range(num_colors)
    nodes = g._nodes.keys()  
    lp = LpProblem("Coloring_Problem",LpMinimize)
    xij = LpVariable.dicts("x",(nodes, colors),0,1,LpInteger) 
    wj = LpVariable.dicts("w",colors,0,1,LpInteger) 
    obj = lpSum(wj[j] for j in colors) 
    lp += obj, "Objective Function"

    #1 color/node
    for n in nodes: 
        total_colors = 0 
        for c in colors: 
            total_colors += xij[n][c] 
        lp += total_colors==1

    #Adjacent nodes aren't the same color.
    for k,v in g._edges.items(): 
        for j in g._edges[k]: 
            #Make sure pair i,j are not the same colors 
            for c in colors: 
                lp += xij[k.name][c] + xij[j.name][c] <= 1
    #TODO: Something to relate x and w 
    for i in nodes: 
        for c in colors: 
            lp += xij[i][c] <= wj[c]

    #Can't be more than 10 colors 
    lp += lpSum(wj[c] for c in colors) <= num_colors 
    lp.solve()
    print("Sol: " + str(LpStatus[lp.status])) 
    print(value(lp.objective)) 
    for c in colors: 
        print(wj[c].value())
    # print(xij)
    for i in nodes: 
        for j in colors: 
            if xij[i][j].value() == 1: 
                print(i + " assigned to color: " + str(j)) 
    # for c in colors: 

# solve_graph(5) 
#Problem 2: Add in some weights, solve the color distribution problem given a target color 
#Each color is meant to represent a register, and let the final color represent memory. 
#Each Node will have a #of operations associated with it. The total cost for each node is formulated as 
#Sometimes it might be worth it to have more colors than necessary, so that we avoid the unecessary cost made by memory. 

np.random.seed(42314) 
operations = {}
mem_cost = 2 #Lets just say memory accesses will cost 2* the clock cycles of other things
for n in g._nodes.keys(): 
    #can have anywhere bewteen 1 and 5 operations
    operations[n] = np.random.randint(1,5)


def solve_weighted_graph(num_colors): 
    colors = range(num_colors)
    nodes = g._nodes.keys()  
    lp = LpProblem("Coloring_Problem",LpMinimize)
    xij = LpVariable.dicts("x",(nodes, colors),0,1,LpInteger) 
    wj = LpVariable.dicts("w",colors,0,1,LpInteger) 

    obj = 0 
    for n in nodes: 
        for c in colors: 
            mem_type = mem_cost if c == 0 else 1 
            obj += xij[n][c] * operations[n] * mem_type 
    lp += obj, "Objective Function"

    for n in nodes: 
        total_colors = 0 
        for c in colors: 
            total_colors += xij[n][c] 
        lp += total_colors==1

    #Modify: Adjacent nodes aren't the same color. Unless it occupies a memory slot 
    for k,v in g._edges.items(): 
        for j in g._edges[k]: 
            for c in colors[1:]: 
                lp += xij[k.name][c] + xij[j.name][c] <= 1

    #Same deal only need to check non-memory slots 
    for i in nodes: 
        for c in colors[1:]: 
            lp += xij[i][c] <= wj[c]

    #Can't be more than 10 colors 
    lp += lpSum(wj[c] for c in colors) <= num_colors  
    lp.solve()
    print("Sol: " + str(LpStatus[lp.status])) 
    print(value(lp.objective))
    print("Operations: " + str(operations)) 
    for i in nodes: 
        for j in colors: 
            if xij[i][j].value() == 1: 
                print(i + " assigned to color: " + str(j)) 
    

def main():
    if len(sys.argv) != 3:
        print("Usage: script.py <'reg-alloc'/'general'> <integer>")
        sys.exit(1)

    mode = sys.argv[1]
    num_colors = 0 
    try:
        num_colors = int(sys.argv[2])
    except ValueError:
        print("Second argument must be an integer.")
        sys.exit(1)

    if mode == "reg-alloc":
        solve_weighted_graph(num_colors) 
    elif mode == "general":
        solve_graph(num_colors) 
    else:
        print("First argument must be 'reg-alloc' or 'general'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
