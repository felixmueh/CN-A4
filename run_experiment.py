#!/usr/bin/env python3
import sys
import os
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


gen_ba_graph(50, 1, 10, "graphs/BA_graph_50_1_10.net")
gen_er_graph(50, 0.1, "graphs/ER_graph_50_0.1.net")
# prepend .. to filepath (not clean but it works)
gen_cm_poisson_graph(50, 1, "../graphs/CM_Poisson_graph_50_1.net")
gen_cm_powerlaw_graph(50, 2.5, 1, "../graphs/CM_Powerlaw_graph_50_2.5_1.net")
print("Done generating graphs.")

simulation_queue = [
    ("graphs/BA_graph_50_1_10.net",  "results/BA_graph_50_1_10", 0.1),
    ("graphs/ER_graph_50_0.1.net", "results/ER_graph_50_0.1", 0.1),
    ("graphs/CM_Poisson_graph_50_1.net", "results/CM_Poisson_graph_50_1", 0.1),
    ("graphs/CM_Powerlaw_graph_50_2.5_1.net", "results/CM_Powerlaw_graph_50_2.5_1", 0.1)
]

import multiprocessing
pool = multiprocessing.Pool()
pool.starmap(run_sis_simulation, simulation_queue)
pool.close()
pool.join()

import matplotlib.pyplot as plt
for _, result_file, mu in simulation_queue:
    with open(result_file, 'r') as f:
        lines = f.readlines()
        x = [float(i) for i in lines[0].split(",")]
        y = [float(i) for i in lines[1].split(",")]
        plt.plot(x, y, label="mu = " + str(mu))
        plt.legend()
        plt.savefig(result_file + ".png")

print("Done!")
