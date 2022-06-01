"""
Code to reduce graphs
"""
import os
import multiprocessing
from typing import Tuple
from glob import glob

import igraph

from graph_reduction.graph import Graph, load_graph


def compute_cliques(instance_file: str, timeout: int, output_file: str):
    """Compute cliques with igraph

    Args:
        instance_file (str): Name of the edgelist file
        timeout (int): Max time to look for the cliques
        output_file (str): File name where the cliques will be listed
    """
    graph_g = igraph.Graph.Read_Edgelist(instance_file, directed=False)

    process = multiprocessing.Process(
        target=graph_g.maximal_cliques, args=(3, 0, output_file)
    )
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process.join()
        print("Cliques partially loaded")


def reduction(instance_name: str, timeout: int) -> Tuple[int, int, int]:
    """Call the different phases of reduction until there is no more possible reduction

    Args:
        instance_name (str): Instance name
        timeout (int): Max time to compute the cliques

    Returns:
        Tuple[int,int,int]: number of vertices in original graph,
                            number of vertices deleted with first reduction,
                            number of vertices deleted with second reduction
    """
    print(instance_name)
    clique_file = f"conversion/{instance_name}.cliques"
    num_reduction: int = 0
    # load the original instance before sorting the vertices by weights
    graph: Graph = load_graph(
        f"wvcp_original/{instance_name}.edgelist",
        f"wvcp_original/{instance_name}.col.w",
    )

    # keep track of the reduction
    nb_vertices = graph.nb_vertices
    nb_reduc_1 = 0
    nb_reduc_2 = 0
    reduc1 = 1
    reduc2 = 1
    while reduc1 or reduc2:
        # sort the nodes of the graph and save weights and edgelist files in conversion/
        graph.convert_to_nodes(
            f"conversion/{instance_name}_{num_reduction}", only_conv_ed_w=True
        )
        # compute the cliques with igraph
        if os.path.exists(clique_file):
            os.remove(clique_file)
        compute_cliques(
            f"conversion/{instance_name}_{num_reduction}.edgelist", timeout, clique_file
        )
        # Unix functions to analyse cliques :
        #   sed 's/[^ ]//g' tmp_cliques/C2000.9.cliques | awk '{print length }' | sort -u
        #   awk '{print NF,$0}' tmp_cliques/C2000.9.cliques | sort -nr | cut -d' ' -f 2-
        # load the graph with custom graph class and compute the reduction
        graph = load_graph(
            f"conversion/{instance_name}_{num_reduction}.edgelist",
            f"conversion/{instance_name}_{num_reduction}.col.w",
        )
        reduc1 = graph.reduction_1(clique_file)
        nb_reduc_1 += reduc1
        reduc2 = graph.reduction_2()
        nb_reduc_2 += reduc2
        num_reduction += 1
        print(f"Reduction {num_reduction} ({reduc1} + {reduc2})")

    if os.path.exists(clique_file):
        os.remove(clique_file)

    # save final reduced graph in wvcp_reduced_graphs/
    graph.convert_to_nodes(f"wvcp_reduced/{instance_name}", only_conv_ed_w=False)
    return nb_vertices, nb_reduc_1, nb_reduc_2


def reduction_all(timeout: int = 10):
    """reduce all instances with a edgelist file in wvcp_original"""
    with open("summary_reduction.csv", "w", encoding="utf8") as output:
        output.write("instance,nb_vertices,first_reduction,second_reduction\n")
        for instance in sorted(glob("wvcp_original/*.edgelist")):
            inst = instance.split("/")[1][:-9]
            nb_vertices, nb_reduc1, nb_reduc2 = reduction(inst, timeout)
            output.write(f"{inst},{nb_vertices},{nb_reduc1},{nb_reduc2}\n")
