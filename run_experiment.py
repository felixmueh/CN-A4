#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import os
import multiprocessing
sys.path.append('network-gen/')

from network_gen import *

import os
os.makedirs("graphs", exist_ok=True)
os.makedirs("results", exist_ok=True)

def run_sis_simulation(in_file, out_file, mu):
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)) + "/network-sis")
    os.system("cargo run --release -- " + "../" + in_file + " ../" + out_file + " " + str(mu))
    os.chdir(current_dir)


def gen_graphs():
    # generate graphs
    print("Generating graphs...")
    gen_ba_graph(10000, 1, 10, "graphs/BA_graph_10000_1_10.net")
    gen_er_graph(10000, 0.1, "graphs/ER_graph_10000_0.1.net")
    # prepend .. to filepath (not clean but it works)
    gen_cm_poisson_graph(10000, 1, "../graphs/CM_Poisson_graph_10000_1.net")
    gen_cm_powerlaw_graph(10000, 2.5, 1, "../graphs/CM_Powerlaw_graph_10000_2.5_1.net")
    print("Done generating graphs.")

simulation_queue = [
    ("graphs/BA_graph_10000_1_10.net",  "results/BA_graph_10000_1_10", 0.1),
    ("graphs/ER_graph_10000_0.1.net", "results/ER_graph_10000_0.1", 0.1),
    ("graphs/CM_Poisson_graph_10000_1.net", "results/CM_Poisson_graph_10000_1", 0.1),
    ("graphs/CM_Powerlaw_graph_10000_2.5_1.net", "results/CM_Powerlaw_graph_10000_2.5_1", 0.1)
]

def sim_graphs():
    pool = multiprocessing.Pool()
    pool.starmap(run_sis_simulation, simulation_queue)
    pool.close()
    pool.join()

def plot_graphs():
    for _, result_file, mu in simulation_queue:
        with open(result_file, 'r') as f:
            lines = f.readlines()
            x = [float(line.split(",")[0]) for line in lines]
            y = [float(line.split(",")[1]) for line in lines]
            plt.plot(x, y)
            plt.title(result_file)
            plt.savefig(result_file + ".png")
            plt.close()

print("Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        gen_graphs()
        sim_graphs()
        plot_graphs()
    if "gen" in sys.argv:
        gen_graphs()
    if "sim" in sys.argv:
        sim_graphs()
    if "plot" in sys.argv:
        plot_graphs()
    print("Done!")
