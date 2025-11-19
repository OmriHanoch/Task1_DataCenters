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

## Example 1: Network Topology Visualization with Link Failures

### Experiment Parameters
- **K-VALUE**: 4 (small topology, 16 hosts total)
- **N-RUNS**: 100 (statistical trials)
- **N-SAMPLES**: 500 (host pairs sampled)
- **FAIL-RATE**: 15.0% (15% of links randomly failed)
- **PENALTY**: 15 hops (disconnection cost)

### Command
```bash
python task1.py --K-VALUE 4 --N-RUNS 100 --N-SAMPLES 500 --FAIL-RATE 15.0 --PENALTY 15
```

### Graph

![image_alt](https://github.com/OmriHanoch/Task1_DataCenters/blob/6da60bd47e50aaa0166e87387eca8822243293a6/%D7%A6%D7%99%D7%9C%D7%95%D7%9D%20%D7%9E%D7%A1%D7%9A%202025-11-19%20161136.png)

### Description & Observations

**Topology Structure:**
The visualization shows a **k-ary Fat-Tree with K=4** organized in four hierarchical layers:

1. **Core Layer (Top - Blue)**: 4 core switches (C_0, C_1, C_2, C_3) that interconnect all pods
2. **Aggregation Layer (Green)**: 8 aggregation switches (A_0_0, A_0_1, ... A_3_0, A_3_1) – 2 per pod
3. **Edge Layer (Orange)**: 8 edge switches (E_0_0, E_0_1, ... E_3_0, E_3_1) – 2 per pod
4. **Host Layer (Gray)**: 16 hosts (H_0_H_1, ... H_14_H_15) – 2 hosts per edge switch

**Link Failures (Red Dashed Lines):**
The red dashed lines represent the **8 links that were randomly removed** during the 15% failure rate simulation:
- C_2 → A_3_1 (core-to-aggregation link failure)
- A_1_1 → E_1_0 and E_1_1 (aggregation-to-edge failures in pod 1)
- A_2_0 → E_2_1 (aggregation-to-edge failure in pod 2)
- E_0_1 → H_2_H_3 (edge-to-host failure in pod 0)
- E_3_1 → H_14_H_15 (edge-to-host failure in pod 3)

**Significance:**
At 15% failure rate, the network experiences **significant disruption**:
- Some host groups (e.g., hosts connected to E_0_1 and E_3_1) become **isolated** – they cannot reach other pods
- Remaining paths are **longer and less optimal** – traffic must detour through surviving links
- The **redundancy is nearly saturated** – the Fat-Tree's built-in parallel paths are exhausted
- Real-world impact: Host-to-host communication degradation, potential data loss

**Key Insight:** The Fat-Tree remains connected at 15% failures, but **large segments are isolated from cross-pod communication**, illustrating the critical failure threshold discussed in the robustness analysis.
Experiment Parameters:Network Size (--K-VALUE 8): The Fat-Tree was built using $K=8$ switches (supporting 128 Hosts). This size was chosen because it is large enough to demonstrate the benefits of redundancy while remaining computationally feasible for extensive statistical analysis.Statistical Trials (--N-RUNS 100): For each failure rate tested (0% to 15%), 100 independent trials were run. This high number was chosen to minimize statistical noise and ensure that the resulting average reachability is accurate and reliable.Sample Size (--N-SAMPLES 500): In each trial, 500 random host pairs were sampled. This is sufficient to represent the entire network's performance, capturing both inter-pod and intra-pod traffic patterns.

## Example 2: Robustness Analysis – Reachability & Path Length vs. Failure Rate

### Experiment Parameters
- **K-VALUE**: 4 (small topology, 16 hosts total)
- **N-RUNS**: 100 (independent statistical trials per failure rate)
- **N-SAMPLES**: 500 (random host pairs sampled per trial)
- **FAIL-RATE**: Tests 0% to 15% failure rates
- **PENALTY**: 15 hops (cost for disconnected pairs)

### Command
```bash
python task1.py --K-VALUE 4 --N-RUNS 100 --N-SAMPLES 500 --FAIL-RATE 15.0 --PENALTY 15
```

### Graph

![image_alt](https://github.com/OmriHanoch/Task1_DataCenters/blob/1788f101f80cb8a158dfe6b28690e85e3d505c77/%D7%A6%D7%99%D7%9C%D7%95%D7%9D%20%D7%9E%D7%A1%D7%9A%202025-11-19%20161225.png)

### Description & Observations

**Experimental Design:**
This analysis measures **two complementary metrics** across a range of failure rates to assess network degradation:

1. **Reachability (%)** – Red curve, left Y-axis:
   - Percentage of sampled host pairs that remain connected
   - 100% = all hosts can reach each other
   - Measures **connectivity loss** as links fail

2. **Average Path Length (hops)** – Blue curve, right Y-axis:
   - For connected pairs: shortest path length
   - For disconnected pairs: penalty of 15 hops (higher penalty emphasizes isolation cost)
   - Measures **routing efficiency** (longer paths = less optimal)

**Observed Results (from actual data):**

**Stage 1 (0% failure rate):**
- **Reachability**: 100% (perfect connectivity)
- **Path Length**: ~5.5 hops (baseline optimal routing for K=4)
- **Interpretation**: Healthy network with all paths available

**Stage 2 (1–3% failure rate):**
- **Reachability**: Gradual decline (100% → ~95%)
- **Path Length**: Slow increase (5.5 → 5.8 hops)
- **Interpretation**: Network redundancy absorbs failures; minimal degradation

**Stage 3 (4–10% failure rate):**
- **Reachability**: Moderate decline (95% → ~80%)
- **Path Length**: Moderate increase (5.8 → 7.5 hops)
- **Interpretation**: Redundancy becoming strained; more path detours needed

**Stage 4 (10–15% failure rate):**
- **Reachability**: Sharp drop (80% → ~67%)
- **Path Length**: Steep jump (7.5 → 9.0 hops)
- **Interpretation**: **Critical saturation reached**; parallel paths exhausted, large portions fragmented

**Significance of Results:**

1. **Non-linear degradation**: Network degradation accelerates as failures increase
   - 0–3%: Stable redundancy (minimal impact)
   - 3–10%: Gradual breakdown (moderate impact)
   - 10–15%: Rapid collapse (severe impact)
   - The curves diverge sharply, showing connectivity loss and routing inefficiency compound

2. **Penalty impact (15 hops)**: 
   - High penalty (15 hops) makes disconnections expensive
   - Path length reaches 9.0 hops at 15% failure – significantly higher than baseline 5.5 hops
   - This 63% increase reveals the severe cost of losing connectivity
   - Emphasizes that at high failure rates, isolated hosts are very costly to the network

3. **K=4 small topology resilience**:
   - Smaller networks are less resilient (fewer parallel paths per host pair)
   - At 15% failure: Only ~67% of host pairs connected
   - Network remains functional but severely degraded
   - Demonstrates importance of topology scale in robustness

**Real-World Implications:**
- Small k-ary Fat-Trees (K=4) maintain >80% reachability up to ~10% failures
- Beyond 10%, network performance degrades rapidly – urgent intervention needed
- Larger topologies (K=8, K=12) would maintain significantly better connectivity at same failure rates
- For production datacenters, maintain link failure rates <5% for operational safety



## Acknowledgments

This project was developed with assistance from **GitHub Copilot** and **Gemini** AI tools, which provided code generation, optimization, documentation, and debugging support throughout the implementation process.
