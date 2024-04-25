#!/usr/bin/env python3
import sys
import matplotlib.pyplot as plt
import os
import multiprocessing
import numpy as np
import networkx as nx

sys.path.append('network-gen/')
from network_gen import *

import os
os.makedirs("graphs", exist_ok=True)
os.makedirs("results", exist_ok=True)
os.makedirs("plots", exist_ok=True)

exec_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "network-sis/target/release/sis-sim")

n_sim = 5000

mus = [0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0]

sim_tasks = [
    ("BA", gen_ba_graph, [1000, 1, 10], mus),
    ("ER", gen_er_graph, [1000, 0.1], mus),
    ("WS", gen_ws_graph, [1000, 20, 0.1], mus),
    ("CM-Poisson", gen_cm_poisson_graph, [1000, 12], mus),
    ("CM-Powerlaw", gen_cm_powerlaw_graph, [1000, 3, 4], mus)
]

def get_name_mu(sim_task, mu):
    return get_name(sim_task) + f"_mu-{mu}"

def get_name(sim_task):
    param_str = "_".join([str(p) for p in sim_task[2]])
    return f"{sim_task[0]}_{param_str}"

def get_graph_file_path(sim_task, i):
    # without mu
    param_str = "_".join([str(p) for p in sim_task[2]])
    return f"graphs/{sim_task[0]}_{param_str}-{i}.net"

def get_result_file_path(sim_task, i, mu):
    name = get_name_mu(sim_task, mu)
    return f"results/{name}-{i}.csv"

def get_plot_file_path(sim_task, mu):
    name = get_name_mu(sim_task, mu)
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

def validate_graph(graph_path):
    G = nx.read_pajek(graph_path)
    G = nx.Graph(G)
    has_self_loops = False
    for u, v in G.edges():
        if u == v:
            print(f"Graph {graph_path} has self-loops")
            return False
    n_components = nx.number_connected_components(G)
    if n_components != 1:
        print(f"Graph {graph_path} has {n_components} components")
        return False
    return True


def build_rust_lib():
    current_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)) + "/network-sis")
    os.system("cargo build --release")
    os.chdir(current_dir)
build_rust_lib()

def run_sis_simulation(in_file, out_file, mu):
    os.system(f"{exec_path} {in_file} {out_file} {mu}")

def validate_graphs():
    print("Validating graphs...")
    pool = multiprocessing.Pool()
    handles = []
    for sim_task in sim_tasks:
        for i in range(n_sim):
            handles.append(
                pool.apply_async(validate_graph, [get_graph_file_path(sim_task, i)])
            )
    pool.close()
    pool.join()
    for handle in handles:
        if not handle.get():
            print("Validation failed!")
            return False
    print("Validation successful!")
    return True

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
        results_mu = []
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
            results_mu.append((mu, mean, std))
            fig, ax = plt.subplots()
            ax.plot(x, mean, label="Mean")
            ax.fill_between(x, mean-std, mean+std, alpha=0.5)
            plot_title = get_name_mu(sim_task, mu) + f" Mean over {n_sim} simulations\nShaded area is the standard deviation"
            ax.set_title(plot_title)
            fig.savefig(get_plot_file_path(sim_task, mu) + f"-mean-{n_sim}.png")
            plt.close(fig)
        fig, ax = plt.subplots()
        for mu, mean, std in results_mu:
            ax.plot(x, mean, label=f"Mu={mu}")
            # ax.fill_between(x, mean-std, mean+std, alpha=0.5)
        plot_title = get_name(sim_task) + f" Mean over {n_sim} simulations."
        ax.set_title(plot_title)
        ax.legend()
        fig.savefig(get_plot_file_path(sim_task, "all") + f"-mean-{n_sim}.png")
        plt.close(fig)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        gen_graphs()
        validate_graphs()
        sim_graphs()
        plot_graphs()
    if "gen" in sys.argv:
        gen_graphs()
    if "validate" in sys.argv:
        validate_graphs()
    if "sim" in sys.argv:
        sim_graphs()
    if "plot" in sys.argv:
        plot_graphs()
    print("Done!")
