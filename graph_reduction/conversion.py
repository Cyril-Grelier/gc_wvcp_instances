"""
Class graph is approximately the same as in reduction.py
to copy paste and use files easily in other projects
"""
from typing import List, Tuple, Dict
import bisect
from glob import glob

from instances.graph_reduction.graph import Graph, load_graph


def load_conversion(
    file_name: str,
) -> Tuple[Dict[int, int], List[int], Dict[int, int]]:
    """Load conversion file to convert reduced solution to original one

    :param instance_name: name of the instance (without the _r)
    :type instance_name: str
    :return: different_number, greedy and same_color structures to convert the solution
    :rtype: Tuple[Dict[int, int], List[int], Dict[int, int]]
    """
    with open(file_name, "r", encoding="utf8") as file:
        different_number: Dict[int, int] = {}
        greedy: List[int] = []
        same_color: Dict[int, int] = {}
        for line in file.readlines():
            if line[0] == "d":
                _, number1, number2 = line.split()
                different_number[int(number1)] = int(number2)
            elif line[0] == "g":
                _, number = line.split()
                greedy.append(int(number))
            elif line[0] == "s":
                _, number1, number2 = line.split()
                same_color[int(number1)] = int(number2)
    return different_number, greedy, same_color


class Solution:
    """Representation of a solution"""

    def __init__(
        self,
        graph: Graph,
        colors: List[int],
        conversion: Tuple[Dict[int, int], List[int], Dict[int, int]],
    ):
        if conversion:
            different_number, greedy, same_color = conversion
        else:
            different_number = {v: v for v in range(graph.nb_vertices)}
            greedy = []
            same_color = dict()
        self.graph: Graph = graph
        self.nb_colors = max(colors) + 1
        # List of vertices of each colors (nb_colors x nb_vertices_per_color)
        self.color_vertices: List[List[int]] = [[] for _ in range(self.nb_colors)]
        # Colors for each vertices (nb_vertices)
        self.colors: List[int] = [-1] * graph.nb_vertices
        # Conflicts of each vertices for each colors (nb_colors x nb_vertices)
        self.conflicts_colors: List[List[int]] = [
            [0] * self.graph.nb_vertices for _ in range(self.nb_colors)
        ]
        # List of weights in each colors (nb_colors x nb_vertices_per_color)
        self.colors_weights: List[List[int]] = [[] for _ in range(self.nb_colors)]
        # Current score
        self.current_score: int = 0
        for old, new in different_number.items():
            self.add_vertex_to_color(old, colors[new])
        for vertex1, vertex2 in same_color.items():
            self.add_vertex_to_color(vertex1, self.colors[vertex2])

        score_before = self.current_score
        greedy.sort(
            key=lambda vertex: (graph.weights[vertex], len(graph.neighborhood[vertex]))
        )
        for vertex in greedy:
            possible_colors = [
                color
                for color in range(len(self.conflicts_colors))
                if self.conflicts_colors[color][vertex] == 0
                and self.get_delta_score(vertex, color) == 0
            ]
            if not possible_colors:
                raise Exception(
                    "problem during placement of reduced vertices : creation of new color"
                )
            color = (
                possible_colors[0] if possible_colors else len(self.conflicts_colors)
            )

            self.add_vertex_to_color(vertex, color)
            if score_before < self.current_score:
                raise Exception(
                    "problem during placement of reduced vertices : score increase"
                )

    def add_vertex_to_color(self, vertex: int, color: int) -> None:
        """
        Add the vertex to its new color

        :param vertex:
        :param color:
        """
        assert self.colors[vertex] == -1, f"vertex {vertex} color already set"
        assert color != -1, "can't add vertex to no color"
        assert len(self.colors_weights) == len(self.conflicts_colors)
        assert (
            len(self.conflicts_colors) <= color
            or self.conflicts_colors[color][vertex] == 0
        ), f"conflicts on the color {color} for vertex {vertex}"
        self.current_score += self.get_delta_score(vertex, color)
        # increase the number of conflict with the neighbors
        for neighbor in self.graph.neighborhood[vertex]:
            self.conflicts_colors[color][neighbor] += 1

        # insert the vertex in the existing color
        bisect.insort(self.colors_weights[color], self.graph.weights[vertex])
        bisect.insort(self.color_vertices[color], vertex)
        # Set the color of the vertex
        self.colors[vertex] = color

    def get_delta_score(self, vertex: int, color: int) -> int:
        """
        Compute the difference on the score if the vertex is move to the color

        :param vertex: the vertex to move
        :type vertex: int
        :param color: the new color
        :type color: int
        :return: the difference on the score if the vertex is set to the color
        """
        vertex_weight: int = self.graph.weights[vertex]
        # if the new color is empty
        if (len(self.colors_weights) <= color) or (not self.colors_weights[color]):
            # the delta is the weight of the vertex
            return vertex_weight

        # if the vertex is heavier than the heaviest of the new color class
        if vertex_weight > self.colors_weights[color][-1]:
            # the delta is the difference between the vertex weight and the heavier vertex
            return vertex_weight - self.colors_weights[color][-1]
        return 0

    def check_solution(self, score_val: int) -> None:
        """
        Check if the current score is correct depending on colors list
        """
        score = 0
        max_colors_weights: List[int] = [0] * self.nb_colors
        for vertex in range(self.graph.nb_vertices):
            color: int = self.colors[vertex]
            if color == -1:
                continue

            assert (
                0 <= color < self.nb_colors
                and self.conflicts_colors[color][vertex] == 0
            ), (
                f"color {color} not in the range [0, {self.nb_colors}[ "
                f"or conflict on the color for the vertex ({self.conflicts_colors[color][vertex]})"
            )

            weight: int = self.graph.weights[vertex]

            if max_colors_weights[color] < weight:
                max_colors_weights[color] = weight

            for neighbor in self.graph.neighborhood[vertex]:
                assert (
                    color != self.colors[neighbor]
                ), f"{vertex} and {neighbor} (neighbors) share the same color ({color})"

        for col in range(self.nb_colors):
            assert len(self.color_vertices[col]) == len(
                self.colors_weights[col]
            ), f"problem in color {col}"
            if not self.color_vertices[col]:
                continue
            assert (
                max_colors_weights[col] == self.colors_weights[col][-1]
            ), f"error in max weight of color {col}"
            score += max_colors_weights[col]

        assert (
            score == self.current_score
        ), f"Problem score {score} vs {self.current_score}"
        assert score == score_val, f"Problem on given score {score} vs {score_val}"


def convert_solution(
    path_to_instance_rep: str, instance: str, colors: List[int], score: int
):
    """Convert a solution from reduced graph to original graph

    Args:
        instance (str): instance name
        colors (List[int]): colors of the vertices
        score (int): score estimated
    """
    conv_files = sorted(
        glob(f"{path_to_instance_rep}/conversion/{instance}_*.conv"),
        key=lambda f: int(f.rsplit("_", 1)[1].split(".")[0]),
        reverse=True,
    )
    edge_files = (
        sorted(
            glob(f"{path_to_instance_rep}/conversion/{instance}_*.edgelist"),
            key=lambda f: int(f.rsplit("_", 1)[1].split(".")[0]),
            reverse=True,
        )[1::]
        + [f"{path_to_instance_rep}/wvcp_original/{instance}.edgelist"]
    )
    weights_files = (
        sorted(
            glob(f"{path_to_instance_rep}/conversion/{instance}_*.col.w"),
            key=lambda f: int(f.rsplit("_", 1)[1].split(".")[0]),
            reverse=True,
        )[1::]
        + [f"{path_to_instance_rep}/wvcp_original/{instance}.col.w"]
    )
    graph = load_graph(
        f"{path_to_instance_rep}/wvcp_reduced/{instance}.edgelist",
        f"{path_to_instance_rep}/wvcp_reduced/{instance}.col.w",
    )
    sol = Solution(graph, colors, None)
    sol.check_solution(score)
    for conv_file, edge_file, weights_file in zip(
        conv_files, edge_files, weights_files
    ):
        graph: Graph = load_graph(edge_file, weights_file)
        conversion = load_conversion(conv_file)
        sol = Solution(graph, colors, conversion)
        sol.check_solution(score)
        colors = sol.colors[:]
