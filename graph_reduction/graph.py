"""
Representation of node and Graph
"""
from typing import List, Tuple, Dict

from dataclasses import dataclass


@dataclass
class Node:
    """Representation of a Node for graph"""

    def __init__(self, number: int, weight: int, neighbors: List[int], reduced: bool):
        self.old_number: int = number
        self.new_number: int = -1
        self.weight: int = weight
        self.neighbors_int: List[int] = neighbors
        self.neighbors_nodes: List[Node] = []
        self.reduced: bool = reduced

    def __repr__(self):
        return (
            f"old_number={self.old_number} new_number={self.new_number} "
            + f"weight={self.weight} degree={len(self.neighbors_int)}"
        )


class Graph:
    """Representation of a graph"""

    def __init__(
        self,
        name: str,
        nb_vertices: int,
        edges_list: List[Tuple[int, int]],
        weights: List[int],
    ):
        self.name: str = name
        self.nb_vertices: int = nb_vertices
        self.weights = weights
        self.adjacency_matrix = [
            [False for _ in range(nb_vertices)] for _ in range(nb_vertices)
        ]
        self.neighborhood: List[List[int]] = [[] for _ in range(nb_vertices)]
        for vertex1, vertex2 in edges_list:
            if not self.adjacency_matrix[vertex1][vertex2]:
                self.adjacency_matrix[vertex1][vertex2] = True
                self.adjacency_matrix[vertex2][vertex1] = True
                self.neighborhood[vertex1].append(vertex2)
                self.neighborhood[vertex2].append(vertex1)
        self.reduced_vertices: List[int] = []
        self.second_reduction: Dict[int, int] = {}

    def delete_vertex(self, vertex: int) -> None:
        """Remove the vertex and add it to the list of reduced vertex

        :param vertex: the vertex to remove
        :type vertex: int
        """
        for neighbor in self.neighborhood[vertex]:
            self.neighborhood[neighbor].remove(vertex)
        self.neighborhood[vertex] = []
        self.reduced_vertices.append(vertex)

    def get_heavier_higher_degree(self) -> Tuple[int, int]:
        """Get the weight and degree of the heavier vertex

        :return: max weight, max degree
        :rtype: Tuple[int, int]
        """
        max_vertex_weight = 0
        max_vertex_degree = 0
        for vertex in range(self.nb_vertices):
            if self.weights[vertex] > max_vertex_weight or (
                self.weights[vertex] == max_vertex_weight
                and len(self.neighborhood[vertex]) > max_vertex_degree
            ):
                max_vertex_weight = self.weights[vertex]
                max_vertex_degree = len(self.neighborhood[vertex])
        return max_vertex_weight, max_vertex_degree

    def reduction_1(self, cliques_file: str) -> int:
        """Apply the reduction based on cliques"""
        cliques: List[List[int]] = []
        # load cliques
        with open(cliques_file, "r", encoding="utf8") as file:
            for line in file.readlines():
                cliques.append(
                    sorted(  # sort the vertices in the clique per weight
                        list(map(int, line.split())),
                        key=lambda v: self.weights[v],
                        reverse=True,
                    )
                )
        if not cliques:
            return 0
        # sort the cliques per total weight
        cliques = sorted(
            cliques,
            key=lambda clique: sum([self.weights[v] for v in clique]),
        )
        # Size largest clique
        size_clique_max: int = max([len(clique) for clique in cliques])
        to_check = []
        to_delete = []
        for vertex in range(self.nb_vertices):
            vertex_degree: int = len(self.neighborhood[vertex])
            # if its degree is lower than the size of the largest clique
            # and its weight is lower than the weight of any
            # vertex of all cliques in the column of its degree
            if vertex_degree < size_clique_max and self.weights[vertex] < max(
                [
                    self.weights[clique[vertex_degree]]
                    for clique in cliques
                    if len(clique) > vertex_degree
                ]
            ):
                # the vertex can be deleted
                to_delete.append(vertex)
            elif not self.neighborhood[vertex]:
                to_check.append(vertex)
        # delete vertices
        for vertex in to_delete:
            self.delete_vertex(vertex)
        max_vertex_weight, max_vertex_degree = self.get_heavier_higher_degree()
        # look for vertices of maximum weight but no neighbors
        to_delete_post = []
        for vertex in to_check:
            if self.weights[vertex] <= max_vertex_weight and max_vertex_degree > 0:
                to_delete_post.append(vertex)
        for vertex in to_delete_post:
            self.delete_vertex(vertex)
        self.reduced_vertices.sort(
            key=lambda v: (
                self.weights[v],
                len(self.neighborhood[v]),
            ),
            reverse=True,
        )
        return len(to_delete) + len(to_delete_post)

    def reduction_2(self) -> int:
        """Apply the reduction based on neighborhood"""
        list_vertices = sorted(
            [v for v in range(self.nb_vertices) if v not in self.reduced_vertices],
            key=lambda v: (self.weights[v], len(self.neighborhood[v])),
        )
        to_delete = []
        # For each free vertex
        for vertex in list_vertices:
            # If the vertex isn't used to reduce an other one
            # (may be useless as we delete with the heavier one)
            if vertex in self.second_reduction.values():
                continue
            # List all neighbors of all neighbors
            neighbors = [set(self.neighborhood[n]) for n in self.neighborhood[vertex]]
            if neighbors:
                # List commun neighbors
                inter = neighbors[0].intersection(*neighbors)
                # Remove conserned vertex from the commun neighbors
                inter.remove(vertex)
                assert not any(n_vertex in self.reduced_vertices for n_vertex in inter)
                # For each commun neighbors sorted by weight and degree
                for n_vertex in sorted(
                    inter,
                    key=lambda v: (self.weights[v], len(self.neighborhood[v])),
                    reverse=True,
                ):
                    # if the neighbor is heavier than the vertex
                    if (
                        self.weights[n_vertex] > self.weights[vertex]
                        or (
                            self.weights[n_vertex] == self.weights[vertex]
                            and len(self.neighborhood[vertex])
                            < len(self.neighborhood[n_vertex])
                        )
                        or (
                            self.weights[n_vertex] == self.weights[vertex]
                            and len(self.neighborhood[vertex])
                            == len(self.neighborhood[n_vertex])
                            and n_vertex < vertex
                        )
                    ):
                        # the vertex can be deleted as it can take the color
                        # of the neighbor without increasing the score
                        self.second_reduction[vertex] = n_vertex
                        to_delete.append(vertex)
                        break
        # delete vertices
        for vertex in to_delete:
            self.delete_vertex(vertex)
        return len(to_delete)

    def convert_to_nodes(self, output_file_base: str, only_conv_ed_w: bool = True):
        """
        Convert graph to node representation before simplifying it and save it in different format
        """
        # Create the nodes
        nodes: List[Node] = [
            Node(
                vertex,
                self.weights[vertex],
                self.neighborhood[vertex][:],
                vertex in self.reduced_vertices,
            )
            for vertex in range(self.nb_vertices)
        ]
        # Add the neighbors to the nodes
        for node in nodes:
            for neighbor in node.neighbors_int:
                if nodes[neighbor].old_number != neighbor:
                    print("error")
            node.neighbors_nodes = [nodes[neighbor] for neighbor in node.neighbors_int]
        # Sort the nodes by weights and degree
        nodes_not_reduced = sorted(
            [node for node in nodes if not node.reduced],
            key=lambda n: (n.weight, len(n.neighbors_int)),
            reverse=True,
        )
        # Gives the new numbers to the nodes
        for i, node in enumerate(nodes_not_reduced):
            node.new_number = i
            assert all(not n.reduced for n in node.neighbors_nodes)
        # Count the edges for DIMACS format
        nb_edges = 0
        for node in nodes_not_reduced:
            node.neighbors_nodes.sort(key=lambda n: n.new_number)
            nb_edges += len(
                [n for n in node.neighbors_nodes if n.new_number < node.new_number]
            )
        # Prepare different format
        txt_col_file = (
            f"c Reduced graph for {self.name} generated by Cyril Grelier\n"
            + f"p edge {len(nodes_not_reduced)} {nb_edges}\n"
        )
        txt_w_col_file = (
            f"c Reduced graph for {self.name} generated by Cyril Grelier\n"
            + f"p edge {len(nodes_not_reduced)} {nb_edges}\n"
        ) + "".join(
            [f"v {node.new_number + 1} {node.weight}\n" for node in nodes_not_reduced]
        )
        if only_conv_ed_w:
            # Prepare text for conversion file
            txt_conv = (
                f"c conversion from graph {self.name} to reduce version\n"
                + "c lines starting with c : comments\n"
                + "c lines starting with d : the first number is the number "
                + "of the vertex in original graph, the second in the reduced graph\n"
                + "c lines starting with g : the vertex can be colored with an existing "
                + "color without increasing the score\n"
                + "c lines starting with s : the first vertex can be colored with the "
                + "color of the second vertex (numbers from original graph)\n"
            )
            for node in nodes:
                if node.reduced:
                    if node.old_number in self.second_reduction:
                        txt_conv += (
                            f"s {node.old_number} "
                            + f"{self.second_reduction[node.old_number]}\n"
                        )
                    else:
                        txt_conv += f"g {node.old_number}\n"
                else:
                    txt_conv += f"d {node.old_number} {node.new_number}\n"
            write_to_file(txt_conv, f"{output_file_base}.conv")
            write_to_file(
                "".join([f"{node.weight}\n" for node in nodes_not_reduced]),
                f"{output_file_base}.col.w",
            )
            write_to_file(
                "".join(
                    [
                        f"{node.new_number} {n_node.new_number}\n"
                        for node in nodes_not_reduced
                        for n_node in node.neighbors_nodes
                        if node.new_number < n_node.new_number
                    ]
                ),
                f"{output_file_base}.edgelist",
            )
        else:
            nb_edges_v = 0
            for node in nodes_not_reduced:
                for n_node in node.neighbors_nodes:
                    if node.new_number < n_node.new_number:
                        line = f"e {node.new_number +1 } {n_node.new_number + 1}\n"
                        txt_col_file += line
                        txt_w_col_file += line
                        nb_edges_v += 1
            assert nb_edges == nb_edges_v

            write_to_file(txt_col_file, f"{output_file_base}.col")
            write_to_file(txt_w_col_file, f"{output_file_base}.wcol")
            write_to_file(
                "".join([f"{node.weight}\n" for node in nodes_not_reduced]),
                f"{output_file_base}.col.w",
            )
            write_to_file(
                "".join(
                    [
                        f"{node.new_number} {n_node.new_number}\n"
                        for node in nodes_not_reduced
                        for n_node in node.neighbors_nodes
                        if node.new_number < n_node.new_number
                    ]
                ),
                f"{output_file_base}.edgelist",
            )


def load_graph(instance_file: str, instance_weights_file: str) -> Graph:
    """
    Load graph file

    :param instance_file: file containing the instance (edge list file)
    :param instance_weights_file: file containing the weights of the instance (col.w file)
    :return: graph from the file
    """
    with open(instance_file, "r", encoding="utf8") as file:
        edges_list: List[Tuple[int, int]] = []
        nb_edges: int = 0
        for line in file.readlines():
            vertex1, vertex2 = sorted(list(map(int, line.split())))
            nb_edges += 1
            edges_list.append((vertex1, vertex2))
    with open(instance_weights_file, "r", encoding="utf8") as file:
        weights = list(map(int, file.readlines()))
    return Graph(instance_file.split("/")[-1][:-9], len(weights), edges_list, weights)


def write_to_file(table: str, file: str) -> None:
    """Write the table in the file (overwrite it if exist)

    :param table: The table to save
    :type table: List[str]
    :param file: file to write
    :type file: str
    """
    with open(file, "w", encoding="utf8") as file_:
        for line in table:
            file_.write(line)
