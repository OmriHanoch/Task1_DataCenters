This project implements and analyzes a k-ary Fat-Tree network topology using Python and NetworkX.
The script generates the topology, models random link failures, and performs a statistical analysis on the resulting network performance.
The code implements a three-tier hierarchical structure (Core, Aggregation, Edge) defined by the parameter $k$ (the number of ports per switch).

The following libraries must be installed:
pip install networkx matplotlib numpy


The command-line interface (CLI) for running the analysis is handled by the task1.py script using the argparse module. The CLI allows users to control the network's scale, statistical rigor, failure conditions, and metric weighting. The general structure of the command is python [task1.py](http://_vscodecontentref_/2) --K-VALUE <k> --N-RUNS <trials> --N-SAMPLES <samples> --FAIL-RATE <pct> --PENALTY <penalty>.

Parameter Descriptions:

--K-VALUE defines the network size (k-ary Fat-Tree topology; must be even and ≥ 2). Larger K means more hosts/switches (K=8 supports 128 hosts).
--N-RUNS specifies the number of independent statistical trials per failure rate; higher values reduce noise but increase runtime (default 100).
--N-SAMPLES controls how many random host pairs are tested per trial (default 500); for K ≤ 4, all possible pairs are tested exhaustively.
--FAIL-RATE is the link failure probability as a percentage (0.0–100.0); tests network robustness under stress (default 0.0).
--PENALTY is the penalty in hops for disconnected host pairs; emphasizes the cost of isolation (default 10).
Full Example:

python task1.py --K-VALUE 8 --N-RUNS 100 --N-SAMPLES 500 --FAIL-RATE 15.0 --PENALTY 10

This runs a production-grade analysis on a K=8 topology (128 hosts), performs 100 independent trials with 500 sampled host pairs per trial, tests failure rates from 0% to 15%, and applies a 10-hop penalty for disconnections. Expected runtime: 1–2 minutes.
![image_alt]
https://github.com/OmriHanoch/Task1_DataCenters/blob/6da60bd47e50aaa0166e87387eca8822243293a6/%D7%A6%D7%99%D7%9C%D7%95%D7%9D%20%D7%9E%D7%A1%D7%9A%202025-11-19%20161136.png
Experiment Parameters:Network Size (--K-VALUE 8): The Fat-Tree was built using $K=8$ switches (supporting 128 Hosts). This size was chosen because it is large enough to demonstrate the benefits of redundancy while remaining computationally feasible for extensive statistical analysis.Statistical Trials (--N-RUNS 100): For each failure rate tested (0% to 15%), 100 independent trials were run. This high number was chosen to minimize statistical noise and ensure that the resulting average reachability is accurate and reliable.Sample Size (--N-SAMPLES 500): In each trial, 500 random host pairs were sampled. This is sufficient to represent the entire network's performance, capturing both inter-pod and intra-pod traffic patterns.
![image_alt](https://github.com/OmriHanoch/Task1_DataCenters/blob/1788f101f80cb8a158dfe6b28690e85e3d505c77/%D7%A6%D7%99%D7%9C%D7%95%D7%9D%20%D7%9E%D7%A1%D7%9A%202025-11-19%20161225.png)
The quantitative analysis was performed to define the structural limits of the Fat-Tree's fault tolerance, confirming the design's effectiveness. While the network demonstrates near-perfect stability at low failure rates, the crucial results emerge in the 8% to 15% range, which represents exceptionally high stress not typically seen in production environments. Specifically, the data shows that beyond approximately 8% failure, the Reachability Percentage drops sharply (e.g., to 70%-80%), as observed in the graph. This signifies the critical breaking point where the network's built-in redundancy (the parallel paths) is finally overwhelmed, and a sufficient number of links have failed simultaneously to structurally isolate large host segments. The analysis thus validates that the Fat-Tree provides exceptional resilience, functionally operating well past the point of ordinary component failure.
