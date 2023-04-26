from socha import *
import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import time
import copy


# ////////////////     TO DO     ////////////////

'''
- draw only important edges (in the moment no edges) > edgelist + draw argument "arc" (for important edges no curves + myb no arrows but players and player paths are different to normal paths)
edgelist map
'''

# ////////////////    PACKAGE    ////////////////

class YoGraph:

    def __init__(self) -> None:

        self.G = nx.DiGraph()

        # if game should be drawn + some drawing calculations made
        self.visual_game = False

        # some draw parameters
        self.node_pos_map = {}
        self.node_label_map = {}
        self.node_label_pos_map = {}
        self.node_color_map = []
        self.edge_color_map = []
    
    def cart_coord_to_node(self, c: CartesianCoordinate) -> str:
        '''
        converts given CartesianCoordinate c to node str
        '''
        
        return str(c.x) + ' ' + str(c.y)
    
    def hex_coord_to_node(self, h: HexCoordinate) -> str:
        '''
        converts given HexCoordinate h to node str
        '''

        return self.cart_coord_to_node(h.to_cartesian())
    
    def node_to_cart_coord(self, n: str) -> CartesianCoordinate:
        '''
        converts given node str n to CartesianCoordinate
        '''

        return CartesianCoordinate(int(n[0]), int(n[-1]))
    
    def node_to_hex_coord(self, n: str) -> HexCoordinate:
        '''
        converts given node str n to HexCoordinate
        '''
        
        return self.node_to_cart_coord(n).to_hex()

    def full_construct_from_board(self, board: list[list[Field]]) -> 'YoGraph':
        '''
        constructs entire YoGraph from given board, returns YoGraph object
        '''
        
        # new object
        B = YoGraph()

        # for every field
        for i in board:
            for j in i:

                # if smth on field
                if not (j.fish == 0 and j.penguin == None):

                    # create attributes
                    x = j.coordinate.to_cartesian().x   # x coord
                    y = j.coordinate.to_cartesian().y   # y coord
                    n = str(x) + ' ' + str(y)           # node name
                    s = 0 if y % 2 == 0 else 0.5        # shift (x axis) for pattern
                    p = (x + s, 7 - y + 1)              # node pos
                    f = j.fish                          # fish int
                    t = j.get_team()                    # team
                    c = '#' + hex(8 - f * 2)[2] + '0' + hex(16 - f * f)[2] + '0' + 'ff' if t == None \
                        else '#00bb00' if t.value == 'ONE' else '#bb00bb'

                    # add node with attributes
                    B.G.add_node(n,
                                 pos    = p,
                                 color  = c,
                                 cart   = j.coordinate.to_cartesian(),
                                 hex    = j.coordinate,
                                 fish   = f,
                                 team   = t
                                 )

        # edges
        B.add_all_edges_to_nodes()

        return B

    def nodes_in_dir_no_edges(self, h: HexCoordinate, v: Vector, i: int = 1) -> list[tuple[str, int]]:
        '''
        query all (nodes, length) in Vector() direction v, outgoing from HexCoordinate h on graph self.G, starting at i length
        '''
        
        nodes = []

        # go on until no field
        while True:

            # get node from hex and vector
            new_node_hex = h.add_vector(v.scalar_product(i))
            new_node_name = str(new_node_hex.to_cartesian().x) + ' ' + str(new_node_hex.to_cartesian().y)

            # check if not node exists > break
            if not (self.G.has_node(new_node_name)):
                break
            
            # append (node, vector len)
            nodes.append((new_node_name, i))
            i += 1

        return nodes

    def add_all_edges_to_nodes(self) -> None:
        '''
        adds all edges to nodes of Graph self.G according to penguin movement rules
        '''

        # get hex coords of all nodes
        for n, d in self.G.nodes.data():
            h = d['hex']

            # for all vector directions
            for v in Vector().directions:
                
                # get nodes in that direction and add edges for all nodes
                nodes = self.nodes_in_dir_no_edges(h, v)
                for m in nodes: 
                    self.G.add_edge(n, m[0], 
                        #color=d['color'],
                        color='#000000',
                        vector=v,
                        vector_len=m[1]
                    )

    def generate_maps(self,
                      do_node_pos:              bool = True,
                      do_node_label:            bool = True,
                      do_node_label_pos:        bool = True,
                      do_node_color_map:        bool = True,
                      do_edge_color_map:        bool = True,
                      ) -> None:
        '''
        generates all maps (for graph drawing) for given graph self.G according to "activated" maps (standard all on)
        (except edgelist colors)
        '''
        
        # node positions
        if do_node_pos: self.node_pos_map = nx.get_node_attributes(self.G, 'pos')

        # node labels (fish or team)
        if do_node_label:
            for k in self.G.nodes:
                if (self.G.nodes[k]['fish'] != 0):
                    self.node_label_map[k] = self.G.nodes[k]['fish']
                else:
                    self.node_label_map[k] = self.G.nodes[k]['team'].value

        # node label positions
        if do_node_label_pos:
            for k, v in self.node_pos_map.items():
                self.node_label_pos_map[k] = (v[0], v[1] - 0.25)

        # node / edge colors
        if do_node_color_map: self.node_color_map = list(nx.get_node_attributes(self.G, 'color').values())
        if do_edge_color_map: self.edge_color_map = list(nx.get_edge_attributes(self.G, 'color').values())

    def make_move(self, m: Move) -> None:
        '''
        performs given move m on graph
        '''

        # to field
        to_n = self.hex_coord_to_node(m.to_value)
        self.G.nodes[to_n]['fish']  = 0
        self.G.nodes[to_n]['team']  = m.team_enum
        self.G.nodes[to_n]['color'] = '#00bb00' if m.team_enum.value == 'ONE' else '#bb00bb'
        edges = self.G.edges(to_n)
        for e in edges:
            self.G.edges[e]['color'] = self.G.nodes[to_n]['color']

        self.remove_over_edges(to_n)
        self.remove_to_edges(to_n)

        # from field
        if m.from_value != None:
            from_n = self.hex_coord_to_node(m.from_value)
            self.G.remove_node(from_n)

    def remove_over_edges(self, n) -> None:
        '''
        removes all edges going over node n
        '''

        # use undirected version of graph, because else he does not remove "to_edges" if they are from player spots
        UG = self.G.to_undirected()
        
        # list of neighbors
        neighbors = list(UG.neighbors(n))

        for nei in neighbors:
            # hex coord of neighbor
            nei_hex: HexCoordinate = self.G.nodes[nei]['hex']

            # reverse edge
            edge = self.G.edges[nei, n]

            # get nodes via edge vector and vector length + 1
            nodes = self.nodes_in_dir_no_edges(nei_hex, edge['vector'], edge['vector_len'] + 1)

            # reverse edge & remove (need try because of UG this edge might not exist)
            for m in nodes:
                try:
                    self.G.remove_edge(nei, m[0])

                except: pass

    def remove_to_edges(self, n) -> None:
        '''
        removes all edges going to node n
        '''

        # use undirected version of graph, because else he does not remove "to_edges" if they are from player spots
        UG = self.G.to_undirected()

        # list of neighbors
        neighbors = list(UG.neighbors(n))

        # reverse edge & remove
        for nei in neighbors:
            try:
                self.G.remove_edge(nei, n)
            except: pass

    def generate_edgelist(self) -> None:

        pass

    def possible_moves_team(self, team: TeamEnum) -> list[Move]:
        '''
        returns list of possible moves of given teamEnum
        '''

        team_fields = [n for n, attrdict in self.G.nodes(data=True) if attrdict['team'] == team]
        
        possible_moves = []
        if (len(team_fields) < 4):
            for o in [n for n, attrdict in self.G.nodes(data=True) if attrdict['fish'] == 1]:
                possible_moves.append(Move(team, self.node_to_hex_coord(o), None))
        else:
            for t in team_fields:
                for nei in self.G.neighbors(t):
                    possible_moves.append(Move(team, self.node_to_hex_coord(nei), self.node_to_hex_coord(t)))
        
        return possible_moves

    def copy_graph(self) -> 'YoGraph':
        '''
        deepcopy of self (YoGraph object); changes draw_name to random or given
        '''

        C = copy.deepcopy(self)

        return C

    def get_blob_graph(self) -> 'YoGraph':
        '''
        returns subgraph for blob calculations (without maps)
        '''

        # deepcopy
        C = self.copy_graph()

        # get all nodes that are not blob
        no_blobs = [n for n, attrdict in C.G.nodes(data=True) if attrdict['fish'] in [0, 1]]

        # remove these nodes + "over_edges" ("over_edges" only for non penguin nodes)
        for n in no_blobs:
            if (C.G.nodes[n]['fish'] != 0):
                C.remove_over_edges(n)
            C.G.remove_node(n)
            
        return C

    def draw(self, edge_mode: str = '', curve_mode: float = 0, fish: tuple[int, int] = (0, 0)):
        '''
        draws YoGraph object self
        edge_mode: 'all' for all edges ; 'fast' for important edges ; everything else: no edges
        curve_mode: float of curve strength
        '''
        
        if edge_mode == 'all':
            margin = 0.01
            edgelist = self.G.edges
            edge_color_map = self.edge_color_map
        elif edge_mode == 'fast':
            margin = 0.01
            edgelist = []
            edge_color_map = []
        else:
            margin = 0.1
            edgelist = []
            edge_color_map = []

        # create string from curve input
        curve = 'arc3, rad = ' + str(curve_mode)

        # nodes & edges
        nx.draw_networkx(
            self.G, pos=self.node_pos_map, with_labels=True, font_color='#ffffff', font_size=13,
            node_color=self.node_color_map, node_size=800,
            edgelist=edgelist, edge_color=edge_color_map, width=0.5, connectionstyle=curve,
        )
        
        # node fish/team labels
        nx.draw_networkx_labels(self.G, self.node_label_pos_map, self.node_label_map, font_size=8, font_color='#fff')

        # pyplot stuff idk
        plt.margins(margin)
        plt.ion()
        plt.box(False)
        plt.title(str(fish[0]) + ' | ' + str(fish[1]))
        plt.show()
        plt.pause(len(edgelist) / 400 + 0.5)
        plt.clf()