import numpy as np
import networkx as nx

def mmca(G, beta=0, mu=0, initial_infection=0.2, steps=100):
    probs_infection = np.full(G.number_of_nodes(), initial_infection)

    means = []

    for i in range(steps):

        probs_infection_t1 = probs_infection.copy()

        for node in G.nodes():
            qi = np.prod([1 - (probs_infection_t1[list(G.nodes()).index(neighbor)] * beta) for neighbor in G.neighbors(node)])
            probs_infection[list(G.nodes()).index(node)] = (1 - probs_infection_t1[list(G.nodes()).index(node)]) * (1 - qi) + probs_infection_t1[list(G.nodes()).index(node)] * (1 - mu)

        if i >= steps-2:
            means.append(np.mean(probs_infection))
    
    return np.mean(means)
