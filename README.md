MicrobesFlux 
-----------------

*MicrobesFlux* is a web-based platform designed for

 * genome-scale metabolic model reconstruction; and
 * constraint-based modeling for both metabolic steady and non-steady states.

MicrobesFlux is free, open-source software. It uses the [KEGG](http://www.genome.jp/kegg/) database (KGML and LIGAND) and empowered by cloud computation. It employs state-of-the-art optimization solvers, such as IPOPT, to solve large-scale flux-balance models.

MicrobesFlux processes the following unique characteristics:

 * intuitive and interactive metabolic model reconstruction,
 * users have flexibility to further customize metabolic models,
 * dynamic metabolism modeling support (dFBA), in addition to the static-state metabolism modeling capability (FBA)

Frontend (GWT) and backend (Django) code is stored under website.
The script folder contains scripts for solving optimization problems remotely.
The visualize folder contains files for visualize KGML files.

