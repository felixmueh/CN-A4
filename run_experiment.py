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

exec_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "network-sis/target/release/sis-sim")

n_sim = 100

mus = [0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0]

sim_tasks = [
    ("BA", gen_ba_graph, [1000, 1, 10], mus),
    ("ER", gen_er_graph, [1000, 0.1], mus),
    ("WS", gen_ws_graph, [1000, 20, 0.1], mus),
    ("CM-Poisson", gen_cm_poisson_graph, [1000, 1], mus),
    ("CM-Powerlaw", gen_cm_powerlaw_graph, [1000, 2.5, 1], mus)
]

def get_name(sim_task, mu):
    param_str = "_".join([str(p) for p in sim_task[2]])
    return f"{sim_task[0]}_{param_str}_mu-{mu}"

def get_graph_file_path(sim_task, i):
    # without mu
    param_str = "_".join([str(p) for p in sim_task[2]])
    return f"graphs/{sim_task[0]}_{param_str}-{i}.net"

def get_result_file_path(sim_task, i, mu):
    name = get_name(sim_task, mu)
    return f"results/{name}-{i}.csv"

def get_plot_file_path(sim_task, mu):
    name = get_name(sim_task, mu)
    return f"plots/{name}.png"

def gen_graphs():
    # generate graphs
    print("Generating graphs...")
    pool = multiprocessing.Pool()
    for i in range(n_sim):
        for sim_task in sim_tasks:
            print(f"Generating {get_graph_file_path(sim_task, i)} ...")
            pool.apply_async(sim_task[1], sim_task[2] + [get_graph_file_path(sim_task, i)])
    pool.close()
    pool.join()
    print("Done generating graphs.")

def build_rust_lib():
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)) + "/network-sis")
    os.system("cargo build --release")
    os.chdir(current_dir)
build_rust_lib()

def run_sis_simulation(in_file, out_file, mu):
    os.system(f"{exec_path} {in_file} {out_file} {mu}")

def sim_graphs():
    pool = multiprocessing.Pool()
    for sim_task in sim_tasks:
        for mu in sim_task[3]:
            for i in range(n_sim):
                pool.apply_async(run_sis_simulation, [get_graph_file_path(sim_task, i), get_result_file_path(sim_task, i, mu), mu])
    pool.close()
    pool.join()

def plot_graphs():
    for sim_task in sim_tasks:
        for mu in sim_task[3]:
            results = []
            for i in range(n_sim):
                result_file = get_result_file_path(sim_task, i, mu)
                with open(result_file, 'r') as f:
                    lines = f.readlines()
                    x = [float(line.split(",")[0]) for line in lines]
                    y = [float(line.split(",")[1]) for line in lines]
                    results.append((x, y))
            mean = np.mean([y for x, y in results], axis=0)
            std = np.std([y for x, y in results], axis=0)
            plt.plot(x, mean, label="Mean")
            plt.fill_between(x, mean-std, mean+std, alpha=0.5)
            plot_file = get_plot_file_path(sim_task, mu)
            plt.title(get_name(sim_task, mu) + " Mean over {} simulations".format(n_sim))
            plt.savefig(get_plot_file_path(sim_task, mu) + f"-mean-{n_sim}.png")
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
