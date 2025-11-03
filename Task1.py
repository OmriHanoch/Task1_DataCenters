import networkx as nx
import math
import matplotlib.pyplot as plt
import argparse
import random
import sys
import numpy as np

# --- Utility Functions (Omitted for brevity, assume they are correct) ---

def calculate_fat_tree_params(k):
    """Calculates the structural parameters for a k-port Fat-tree."""
    if k % 2 != 0 or k < 2:
        raise ValueError("k must be an even number greater than or equal to 2.")

    k_half = k // 2
    
    params = {
        'k': k,
        'k_half': k_half,
        'num_pods': k,
        'num_core_switches': k_half * k_half,
        'total_hosts': (k**3) // 4
    }
    return params

def build_fat_tree(k):
    """Builds the Fat-tree topology as a NetworkX graph."""
    try:
        params = calculate_fat_tree_params(k)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    G = nx.Graph() 
    k_half = params['k_half']
    core_switches = []
    pod_switches_data = {} 

    # 1. Create Nodes
    for c_idx in range(params['num_core_switches']):
        node_id = f"C_{c_idx}"
        G.add_node(node_id, type='core', pod=-1) 
        core_switches.append(node_id)

    current_host_idx = 0
    for pod_id in range(params['num_pods']):
        pod_switches_data[pod_id] = {'agg': [], 'edge': [], 'host_to_edge': {}}
        
        # Aggregation Switches
        for a_idx in range(k_half):
            node_id = f"A_{pod_id}_{a_idx}"
            G.add_node(node_id, type='agg', pod=pod_id)
            pod_switches_data[pod_id]['agg'].append(node_id)

        # Edge Switches and Hosts
        for e_idx in range(k_half):
            edge_node_id = f"E_{pod_id}_{e_idx}"
            G.add_node(edge_node_id, type='edge', pod=pod_id)
            pod_switches_data[pod_id]['edge'].append(edge_node_id)

            for h_idx in range(k_half):
                host_node_id = f"H_{current_host_idx}"
                G.add_node(host_node_id, type='host', pod=pod_id, edge_anchor=edge_node_id)
                G.add_edge(edge_node_id, host_node_id, layer='edge_host')
                
                pod_switches_data[pod_id]['host_to_edge'][host_node_id] = edge_node_id
                current_host_idx += 1

    # 2. Create Edges
    for pod_id in range(params['num_pods']):
        agg_switches = pod_switches_data[pod_id]['agg']
        edge_switches = pod_switches_data[pod_id]['edge']

        # A. Aggregation <-> Edge
        for agg_node in agg_switches:
            for edge_node in edge_switches:
                G.add_edge(agg_node, edge_node, layer='agg_edge')

        # B. Core <-> Aggregation (Striping)
        for agg_idx, agg_node in enumerate(agg_switches):
            strip_start_index = agg_idx * k_half
            for core_offset in range(k_half):
                core_idx = strip_start_index + core_offset
                core_node = core_switches[core_idx]
                G.add_edge(agg_node, core_node, layer='agg_core')
                
    G.graph['params'] = params
    G.graph['pod_data'] = pod_switches_data
    return G

def model_link_failures(G, failure_rate_percent):
    """Simulates random link failures."""
    if failure_rate_percent <= 0:
        return []

    all_edges = list(G.edges())
    total_edges = len(all_edges)
    num_to_fail = math.ceil(total_edges * (failure_rate_percent / 100.0))
    
    edges_to_remove = random.sample(all_edges, num_to_fail)

    for u, v in edges_to_remove:
        if G.has_edge(u, v):
            G.remove_edge(u, v)

    return edges_to_remove

# --- Analysis Functions ---

def calculate_avg_path_length(G, host_pairs):
    """
    Calculates the average path length and reachability for the current graph G
    using a fixed list of host_pairs.
    """
    total_path_length = 0
    connected_pairs_count = 0
    num_pairs_checked = len(host_pairs)
    
    if num_pairs_checked == 0:
        return 0.0, 0.0

    for source, target in host_pairs:
        try:
            length = nx.shortest_path_length(G, source=source, target=target)
            total_path_length += length
            connected_pairs_count += 1
        except nx.NetworkXNoPath:
            pass

    if connected_pairs_count == 0:
        return 0.0, 0.0
    
    avg_length = total_path_length / connected_pairs_count
    reachability = (connected_pairs_count / num_pairs_checked) * 100.0
    
    return avg_length, reachability

def run_experiment_cycle(k, fail_rates, N_RUNS=100, N_SAMPLES=500):
    """
    Runs the full statistical experiment for various failure rates.
    """
    results = {'fail_rate': [], 'avg_path': [], 'reachability': []}
    all_hosts = [f"H_{i}" for i in range(calculate_fat_tree_params(k)['total_hosts'])]
    num_hosts = len(all_hosts)
    
    # --- 1. Generate a single, fixed sample set for all runs (Seed 1000) ---
    random.seed(1000) 
    
    if num_hosts <= 16: # K=4 -> Exhaustive Check
        all_possible_pairs = [(source, target) for i, source in enumerate(all_hosts) 
                              for j, target in enumerate(all_hosts) if i != j]
        fixed_host_pairs = all_possible_pairs
        print(f"Sampling: Exhaustive check ({len(fixed_host_pairs)} pairs).")
    else:
        # K > 4 -> Random Sampling
        all_possible_pairs = [(source, target) for i, source in enumerate(all_hosts) 
                              for j, target in enumerate(all_hosts) if i != j] 
        effective_samples = min(N_SAMPLES, len(all_possible_pairs))
        fixed_host_pairs = random.sample(all_possible_pairs, effective_samples)
        print(f"Sampling: Randomly sampled {len(fixed_host_pairs)} fixed pairs.")

    # 2. Loop over each failure rate point (X-axis)
    for rate in fail_rates:
        avg_length_sum = 0
        reachability_sum = 0
        
        for run in range(N_RUNS):
            # 1. Build the base Fat-Tree
            G = build_fat_tree(k)
            
            # 2. Model Failures: Use 'run' number as the seed for unique failure sets
            random.seed(run) 
            model_link_failures(G, rate)
            
            # 3. Analyze the failed graph using the FIXED host pairs list
            length, reachability = calculate_avg_path_length(G, fixed_host_pairs)
            
            avg_length_sum += length
            reachability_sum += reachability
        
        # 4. Store the average results
        avg_length_final = avg_length_sum / N_RUNS
        avg_reachability_final = reachability_sum / N_RUNS
        
        results['fail_rate'].append(rate)
        results['avg_path'].append(avg_length_final)
        results['reachability'].append(avg_reachability_final)
        
        print(f"RATE {rate}%: Avg Path={avg_length_final:.4f}, Reachability={avg_reachability_final:.2f}%")
        
    return results

def draw_fat_tree(G, k, failed_edges=None):
    """Draws the Fat-tree graph with a custom hierarchical layout."""
    
    plt.figure(figsize=(12, 8)) 
    color_map = {'host': '#CCCCCC', 'edge': '#FFC04D', 'agg': '#92D050', 'core': '#9CC2E5'}
    node_colors = [color_map[attr['type']] for n, attr in G.nodes(data=True)]

    # Define Custom Hierarchical Layout (pos)
    pos = {}
    y_core, y_agg, y_edge, y_host = 3.0, 2.0, 1.0, 0.0
    k_half = k // 2
    
    core_nodes = sorted([n for n, attr in G.nodes(data=True) if attr['type'] == 'core'])
    core_x_spacing = 2.0 / (len(core_nodes) + 1)
    for i, node_id in enumerate(core_nodes):
        pos[node_id] = (i * core_x_spacing - 1 + core_x_spacing/2, y_core)
    
    pod_width_scale = 1.0 / k 
    
    for pod_id in range(k):
        pod_center_x = (pod_id + 0.5) * pod_width_scale * 2 - 1 
        
        agg_nodes = sorted([n for n, attr in G.nodes(data=True) if attr['type'] == 'agg' and attr['pod'] == pod_id])
        agg_x_spacing = pod_width_scale / (len(agg_nodes) + 1) * 2 
        for i, node_id in enumerate(agg_nodes):
            pos[node_id] = (pod_center_x - pod_width_scale + (i + 0.5) * agg_x_spacing, y_agg)

        edge_nodes = sorted([n for n, attr in G.nodes(data=True) if attr['type'] == 'edge' and attr['pod'] == pod_id])
        edge_x_spacing = pod_width_scale / (len(edge_nodes) + 1) * 2
        for i, node_id in enumerate(edge_nodes):
            pos[node_id] = (pod_center_x - pod_width_scale + (i + 0.5) * edge_x_spacing, y_edge)
            
        hosts_per_edge = k_half
        all_hosts_in_pod_data = [ (n, attr) for n, attr in G.nodes(data=True) 
                                 if attr['type'] == 'host' and attr['pod'] == pod_id]
        
        all_hosts_in_pod_data.sort(key=lambda item: int(item[0].split('_')[1])) 
        
        for e_idx, edge_node_id in enumerate(edge_nodes):
            start_index = e_idx * hosts_per_edge
            hosts_in_this_edge_range_data = all_hosts_in_pod_data[start_index : start_index + hosts_per_edge]
            
            edge_x_pos = pos[edge_node_id][0]
            host_sub_x_spacing = 0.1 / k_half 
            
            for i, (host_node_id, attr) in enumerate(hosts_in_this_edge_range_data):
                 pos[host_node_id] = (edge_x_pos - (hosts_per_edge - 1) * host_sub_x_spacing / 2 + i * host_sub_x_spacing, y_host)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='gray', width=0.8)
    if failed_edges:
        nx.draw_networkx_edges(G, pos, edgelist=failed_edges, edge_color='red', width=2.0, style='dashed')
    nx.draw_networkx_labels(G, pos, font_size=7, font_weight='bold')

    plt.title(f"Fat-Tree Topology (k={k}) - FAIL RATE: {len(failed_edges)} links removed")
    plt.show()


def visualize_results(results):
    """
    Creates a single plot showing only Reachability (%).
    """
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot 1: Reachability (The ONLY focus)
    color = 'tab:red'
    ax1.set_xlabel('Link Failure Probability (%)')
    ax1.set_ylabel('Reachability (%)', color=color)
    
    # Ensure Y-axis starts at 0%
    ax1.set_ylim(0, 105) 
    
    ax1.plot(results['fail_rate'], results['reachability'], color=color, marker='x', linestyle='--', label='Reachability (%)')
    ax1.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  
    plt.title(f'Fat-Tree Robustness Analysis: Reachability (K={results["params"]["k"]})')
    plt.grid(True)
    ax1.legend(loc='upper right')
    
    plt.show()

# --- Main Execution Block for Analysis ---

def main():
    parser = argparse.ArgumentParser(description="Generate and analyze a k-ary Fat-Tree network topology.")
    
    parser.add_argument('--K-VALUE', type=int, default=8, help="The constant K value for the experiment.")
    parser.add_argument('--N-RUNS', type=int, default=100, help="Number of statistical runs for each data point.")
    parser.add_argument('--N-SAMPLES', type=int, default=500, help="Number of random host pairs to sample when K > 4.")
    parser.add_argument('--FAIL-RATE', type=float, default=0.0, help="The percentage of total links to randomly fail (0.0 to 100.0). Default is 0%.")

    args = parser.parse_args()

    # --- FIX: Correct access to FAIL_RATE and N_RUNS attributes ---
    visual_fail_rate = args.FAIL_RATE
    seed_value = args.N_RUNS # Using N_RUNS as seed for visual state

    # --- 1. Structural Visualization (Single Graph) ---
    graph_viz = build_fat_tree(args.K_VALUE)
    random.seed(seed_value) 
    # Use the correctly named attribute: args.FAIL_RATE
    failed_edges_list_viz = model_link_failures(graph_viz, visual_fail_rate)
    
    print(f"\n--- Structural Visualization (K={args.K_VALUE}) ---")
    print(f"Links Failed in Visualization: {len(failed_edges_list_viz)}")
    
    if args.K_VALUE <= 8:
        draw_fat_tree(graph_viz, args.K_VALUE, failed_edges_list_viz)
    else:
        print("Skipping detailed structural visualization for K > 8 (too dense).")

    # --- 2. Statistical Analysis (Section 5) ---
    
    FAIL_RATES_TO_TEST = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0]
    
    params = calculate_fat_tree_params(args.K_VALUE)
    
    print(f"\n--- Running Statistical Analysis (Section 5) ---")
    print(f"Topology Size: K={args.K_VALUE} (Hosts: {params['total_hosts']})")
    print(f"Runs per Data Point: {args.N_RUNS}")
    
    analysis_results = run_experiment_cycle(
        k=args.K_VALUE, 
        fail_rates=FAIL_RATES_TO_TEST, 
        N_RUNS=args.N_RUNS,
        N_SAMPLES=args.N_SAMPLES
    )
    
    # Attach K value to results for plot title
    analysis_results['params'] = {'k': args.K_VALUE} 

    # Print data summary (required for README.md table)
    print("\n--- Final Analysis Data (for README.md Table) ---")
    print("Failure Rate (%), Avg Path Length (Hops), Reachability (%)")
    for r, p, c in zip(analysis_results['fail_rate'], analysis_results['avg_path'], analysis_results['reachability']):
        print(f"{r:.1f}, {p:.4f}, {c:.2f}")

    # Visualize the results (Reachability Only)
    visualize_results(analysis_results)
    
if __name__ == "__main__":
    main()