#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import os
import multiprocessing
import numpy as np

sys.path.append('network-gen/')
from network_gen import *

import os
os.makedirs("graphs", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("plots", exist_ok=True)

n_sim = 100

def run_sis_simulation(in_file, out_file, mu):
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)) + "/network-sis")
    os.system("cargo build --release")
    os.chdir(current_dir)
    exec_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "network-sis/target/release/sis-sim")
    os.system(f"{exec_path} {in_file} {out_file} {mu}")


def gen_graphs():
    # generate graphs
    print("Generating graphs...")
    pool = multiprocessing.Pool()
    for i in range(n_sim):
        # gen_ba_graph(1000, 1, 10, "graphs/BA_graph_10000_1_10.net")
        # gen_er_graph(1000, 0.1, "graphs/ER_graph_10000_0.1.net")
        # gen_ws_graph(1000, 20, 0.1, "graphs/WS_graph_10000_20_0.1.net")
        # # prepend .. to filepath (not clean but it works)
        # gen_cm_poisson_graph(1000, 1, "../graphs/CM_Poisson_graph_10000_1.net")
        # gen_cm_powerlaw_graph(1000, 2.5, 1, "../graphs/CM_Powerlaw_graph_10000_2.5_1.net")
        pool.apply_async(gen_ba_graph, (1000, 1, 10, f"graphs/BA_graph_1000_1_10-{i}.net"))
        pool.apply_async(gen_er_graph, (1000, 0.1, f"graphs/ER_graph_1000_0.1-{i}.net"))
        pool.apply_async(gen_ws_graph, (1000, 20, 0.1, f"graphs/WS_graph_1000_20_0.1-{i}.net"))
        pool.apply_async(gen_cm_poisson_graph, (1000, 1, f"graphs/CM_Poisson_graph_1000_1-{i}.net"))
        pool.apply_async(gen_cm_powerlaw_graph, (1000, 2.5, 1, f"graphs/CM_Powerlaw_graph_1000_2.5_1-{i}.net"))
    pool.close()
    pool.join()
    print("Done generating graphs.")

simulation_queue = []
for i in range(n_sim):
    simulation_queue.append((f"graphs/BA_graph_1000_1_10-{i}.net",  f"results/BA_graph_1000_1_10-{i}", 0.1))
    simulation_queue.append((f"graphs/ER_graph_1000_0.1-{i}.net", f"results/ER_graph_1000_0.1-{i}", 0.1))
    simulation_queue.append((f"graphs/CM_Poisson_graph_1000_1-{i}.net", f"results/CM_Poisson_graph_1000_1-{i}", 0.1))
    simulation_queue.append((f"graphs/CM_Powerlaw_graph_1000_2.5_1-{i}.net", f"results/CM_Powerlaw_graph_1000_2.5_1-{i}", 0.1))

def sim_graphs():
    pool = multiprocessing.Pool()
    pool.starmap(run_sis_simulation, simulation_queue)
    pool.close()
    pool.join()

def plot_graphs():
    base_results = [
        "results/BA_graph_1000_1_10",
        "results/ER_graph_1000_0.1",
        "results/CM_Poisson_graph_1000_1",
        "results/CM_Powerlaw_graph_1000_2.5_1"
    ]
    for base_result in base_results:
        results = []
        for i in range(n_sim):
            result_file = f"{base_result}-{i}"
            with open(result_file, 'r') as f:
                lines = f.readlines()
                x = [float(line.split(",")[0]) for line in lines]
                y = [float(line.split(",")[1]) for line in lines]
                results.append((x, y))
        mean = np.mean([y for x, y in results], axis=0)
        std = np.std([y for x, y in results], axis=0)
        plt.plot(x, mean, label="Mean")
        plt.fill_between(x, mean-std, mean+std, alpha=0.5)
        plt.title(base_result.replace("results/", "") + " Mean over {} simulations".format(n_sim))
        plt.savefig(base_result.replace("results", "plots") + f"-mean-{n_sim}.png")
        plt.close()

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
