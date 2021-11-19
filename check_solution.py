"""
Use this script to check if a solution is good.
3 parameters : name of the instance, score, colors (separate with ':')

example (good, no output):
    python3 check_solution.py p06 565 0:0:1:1:1:1:2:2:2:2:0:0:4:4:3:3

example (error, print the assertion and exit 1):
    python3 check_solution.py p06 500 0:0:1:1:1:1:2:2:2:2:0:0:4:4:3:3

"""
from instances.graph_reduction.conversion import convert_solution

import sys

instance = sys.argv[1]
score = int(sys.argv[2])
solution = list(map(int, sys.argv[3].split(":")))

try:
    convert_solution(
        path_to_instance_rep=".",
        instance=instance,
        colors=solution,
        score=score,
    )
except AssertionError as e:
    print(e)
    exit(1)
