This project implements and analyzes a k-ary Fat-Tree network topology using Python and NetworkX.
The script generates the topology, models random link failures, and performs a statistical analysis on the resulting network performance.
The code implements a three-tier hierarchical structure (Core, Aggregation, Edge) defined by the parameter $k$ (the number of ports per switch).

The following libraries must be installed:
pip install networkx matplotlib numpy

The command line interface (CLI) for running the analysis is handled by the Task1.py script using the argparse module. The CLI allows users to control the network's scale and the statistical rigor of the experiment. The general structure of the command is python Task1.py --K-VALUE <k> --N-RUNS <trials> --FAIL-RATE <pct>. The core statistical run, necessary for Section 5's analysis, uses the --K-VALUE parameter to define the network size and the --N-RUNS parameter to define the number of statistical trials used for averaging the data points

The quantitative analysis was performed to define the structural limits of the Fat-Tree's fault tolerance, confirming the design's effectiveness. While the network demonstrates near-perfect stability at low failure rates, the crucial results emerge in the 8% to 15% range, which represents exceptionally high stress not typically seen in production environments. Specifically, the data shows that beyond approximately 8% failure, the Reachability Percentage drops sharply (e.g., to 70%-80%), as observed in the graph. This signifies the critical breaking point where the network's built-in redundancy (the parallel paths) is finally overwhelmed, and a sufficient number of links have failed simultaneously to structurally isolate large host segments. The analysis thus validates that the Fat-Tree provides exceptional resilience, functionally operating well past the point of ordinary component failure.
