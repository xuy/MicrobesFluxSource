#!/usr/bin/env python
""" This will plot the network constructed from KGML"""

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot
import matplotlib.pyplot as plt
import sys
import os
import random

def plot_original(pathway, output):
    # G = nx.Graph()
    G=nx.read_adjlist(pathway)
    rlist = set()
    clist = set()
    for n in G.nodes():
        if n[0] == 'C':
            clist.add(n)
        else:
            rlist.add(n)
    # c=[random.random() ]*nx.number_of_nodes(G)
    # nx.draw_networkx_edges(G,alpha=0.4)
    pos=nx.spring_layout(G) # positions for all nodes
    nx.draw_networkx_nodes(G,pos,
                           nodelist=rlist,
                           node_size=0.2,
                           #with_labels=False,
                           node_color='green',
                           alpha=1.0)

    nx.draw_networkx_nodes(G,pos,
                          nodelist=clist,
                          node_color='blue',
                          node_size=1.0,
                          alpha=1.0)

    nx.draw_networkx_labels(G,pos,font_size=5,
                            font_color='red')

    nx.draw_networkx_edges(G,pos)
    print len(G.nodes())
    print len(G.edges())
    plt.axis('off')
    plt.savefig(output + ".svg", )

if __name__ == '__main__':
    if len(sys.argv) < 2: #  or len(sys.argv[1]) != 3:
        print "Use plot.py filename"
        sys.exit(-1)
    else:
        bac_name = sys.argv[1]
        plot_original(bac_name, bac_name+"_plot")
