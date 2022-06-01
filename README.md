# Instances for graph coloring and weighted vertex coloring problem

origin of the files :

    - wvcp_original: http://www.info.univ-angers.fr/pub/hao/wvcp.html
    - graph_coloring : DIMACS Challenge II
    - bandwidth_multicoloring_instances : https://mat.gsia.cmu.edu/COLOR04/
    - given by other teams working on WVCP

wvcp repertories contains all collected graphs and their weights, you can find three types of files:

    - .col files from the DIMACS challenge (vertex numbers start at 1)
    - .edgelist files: each line is an edge between two nodes (vertex numbers start at 0)
    - .col.w files : line 1 is the weight of node 0, line 2 the weight of node 1, ...
    - .wcol files: DIMACS Challenge files + v lines with the weights of each vertex (vertex number starts at 1).

wvcp_original contains the original versions of the files.
wvcp_reduced contains the reduced versions of the files (details about the reduction will be given soon).

The files may have been modified to remove lines, the weights at the end of the .col file removed to generate the .col.w file for example, but all the graphs remain the same (number of nodes and edges, weights,...) if you find an error please inform us.

Exception ! These instances have been added without weights, they are only here for graph coloring problem (GCP) : 

    wvcp_original/DSJR500.1c.col
    wvcp_original/DSJR500.5.col
    wvcp_original/flat300_26_0.col
    wvcp_original/flat300_28_0.col
    wvcp_original/r1000.1c.col
    wvcp_original/r250.5.col


You can find the current best known scores for the wvcp coloring problem in the file best_scores_wvcp.txt, known from [1] and [2] , \* means its the optimal score and - means its the current best score (possibly optimal but not proven). These scores are reported scores, the solutions linked to the score are not always available to validate the score and the time spent to reach these scores depends on the article (1h for the score of [1], up to several days for [2]).

[1] Nogueira, Bruno, Eduardo Tavares, et Paulo Maciel. «Iterated Local Search with Tabu Search for the Weighted Vertex Coloring Problem». Computers & Operations Research 125 (1 janvier 2021): 105087. https://doi.org/10.1016/j.cor.2020.105087.

[2] Goudet, O., Grelier, C., Hao, J.-K., 2021. A deep learning guided memetic framework for graph coloring problems. arXiv:2109.05948 [cs]

DIMAC_large.txt, DIMAC_small.txt, pxx.txt and rxx.txt are the lists of instances used in the state of the art to compare the algorithms. other.txt lists instances in the directory but not currently used for comparison in the state of the art.

To add this module to your project :

    git submodule add https://github.com/Cyril-Grelier/gc_wvcp_instances.git instances

To remove the module from your project :

    git config -f .git/config --remove-section submodule.instances
    git config -f .gitmodules --remove-section submodule.instances
    git add .gitmodules
    git rm --cached instances
    git add .gitmodules
    rm -rf instances
    rm -rf .git/modules/instances

To update :

    cd instances/
    git pull origin main
    cd ..
    git add instances/
    git commit -m "submodule instance updated"
    git push

To prepare python env : (tested with python 3.8)

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirement.txt

To recompute reduction :

     uncomment lines about reduction in main.py
     run :

    	python main.py

To check a reduced graph solution :

    uncomment lines about conversion in main.py
    change instance name, give the solution colors in a list of int and the score
    run :

    	python main.py
