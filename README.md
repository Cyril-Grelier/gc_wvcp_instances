# instances for graph coloring and weighted vertex coloring problem

origin of files :

    - wvcp_original : http://www.info.univ-angers.fr/pub/hao/wvcp.html
    - graph_coloring : DIMACS Challenge II
    - bandwidth_multicoloring_instances : https://mat.gsia.cmu.edu/COLOR04/
    - given by other teams working on the WVCP

wvcp repertories contains all graphs gathered and their weights, you can find three types of files :

    - .col files from DIMACS Challenge (vertices numbers start at 1)
    - .edgelist files : each line is an edge between two nodes (vertices number start at 0)
    - .col.w files : line 1 is the weight of the node 0, line 2 the weight of the node 1 ...
    - .wcol files : DIMACS Challenge files + v lines with the weights of each vertices (vertices numbers start at 1)

wvcp_original contains original versions of the files.
wvcp_reduced contains reduced versions of the files (details will be had soon about the reduction).

Files may have been modified to suppress lines, weights at the end of .col file suppressed to generate .col.w file for example, but all graphs remain the same (number of nodes and edges, weights,...) if you find any mistake please inform us.

DIMAC_large.txt, DIMAC_small.txt, pxx.txt and rxx.txt are the lists of instances used in state of the art to compare algorithm. other.txt list instances in the repertory but currently not used as comparison in the state of the art.

To add theses instances to your project :

    git submodule add https://github.com/Cyril-Grl/gc_wvcp_instances.git instances

To delete theses instances from your project :

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
