# %%


# %%
import heapq
from html import parser
import networkx as nx
import random


# %%



# %%

def parse_clusters_tab(path):
    """
    Parse clusters.tab (or perbin.clusters.tab) file into a list of cluster dicts:
       { "bin": str, "size": int, "vol": int, "phi": float, "nodes": set(int) }
    """
    clusters = []
    with open(path, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue

            parts = line.strip().split("\t")
            if len(parts) < 5:
                continue

            bin_label = parts[0]
            size = int(parts[1])
            vol = int(parts[2])
            phi = float(parts[3])
            nodes = set(map(int, parts[4].split()))

            clusters.append({
                "bin": bin_label,
                "size": size,
                "vol": vol,
                "phi": phi,
                "nodes": nodes
            })

    return clusters


def phi_update(phi_old, vol_old):
    return (phi_old * vol_old + 1) / (vol_old + 1)





def filter_bin(clusters, bin_label):
    """Return only clusters belonging to a specific bin label."""
    return [c for c in clusters if c["bin"] == bin_label]

import random
import networkx as nx


def apply_edge_updates(clusters, u, v):
    """
    Update phi and vol for all clusters affected by new edge (u,v).
    No nodes are added to clusters.
    """
    for c in clusters:
        u_in = (u in c["nodes"])
        v_in = (v in c["nodes"])
        if u_in ^ v_in:  # exactly one endpoint inside
            old_vol = c["vol"]
            c["vol"] = old_vol + 1
            c["phi"] = (c["phi"] * old_vol + 1) / c["vol"]


def safe_add_edge(G, u, v):
    """Add edge (u,v) if not already present. Returns True if added."""
    if G.has_edge(u, v):
        return False
    G.add_edge(u, v)
    return True


def improve_bin(G, clusters, budget=100, only_fallback = False, max_scan=100):
    """
    Improve clusters by adding edges.
    Stops when 'budget' edges have been successfully added.
    Returns: (clusters, stats)
    """
    all_cluster_nodes = set().union(*(c["nodes"] for c in clusters))
    all_graph_nodes = set(G.nodes())
    outside_nodes = list(all_graph_nodes - all_cluster_nodes)

    stats = {"strict_edges": 0, "fallback_edges": 0}
    edges_added = 0

    while edges_added < budget:
        # Always pick cluster with smallest phi
        clusters.sort(key=lambda c: c["phi"])
        A = clusters[0]

        partner_found = False
        if(only_fallback):
            outside_nodes = list(all_graph_nodes - A["nodes"])

      #  Try connecting A to another cluster
        else: #strict edges 
            for B in clusters[1:min(max_scan, len(clusters))]:
                diff_A = list(A["nodes"] - B["nodes"])
                diff_B = list(B["nodes"] - A["nodes"])
                if diff_A and diff_B:
                    u = random.choice(diff_A)
                    v = random.choice(diff_B)
                    added = safe_add_edge(G, u, v)
                    if added:
                        stats["strict_edges"] += 1
                        edges_added += 1
                        apply_edge_updates(clusters, u, v)
                        partner_found = True
                        break  # Only add one edge per iteration

        # Fallback: connect A to outside node
        if not partner_found and outside_nodes:
            u = random.choice(list(A["nodes"]))
            v = random.choice(outside_nodes)
            added = safe_add_edge(G, u, v)
            if added:
                stats["fallback_edges"] += 1
                edges_added += 1
                apply_edge_updates(clusters, u, v)
                outside_nodes.remove(v)

        # If no edge was added, break to avoid infinite loop
        if not partner_found and not outside_nodes:
            break

    return clusters, stats


# %%
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Run my NCP improvement script")
    parser.add_argument("--graph_path", type=str, default="../datasets/facebook/facebook_combined.txt", help="Path to input graph")
    parser.add_argument("--bin", type=str, default="all", help="Bin to process")
    parser.add_argument("--budget", type=int, default=100, help="Number of edges to add")
    parser.add_argument("--only_fallback", action="store_true", help="Use only fallback edges")
    parser.add_argument("--clusters_path", type=str, default="../target/ncp.facebook_combined.perbin.clusters.tab", help="Path to clusters.tab file")
    return parser.parse_args()  # <-- reads the actual command-line input


def main():
    args = parse_args()
    if(args.only_fallback):
        output_path = f'../target/wncp/fallback/facebook_fallback_wncp_{args.budget}.edgelist'
    else:
        output_path = f'../target/wncp/strict/facebook_wncp_{args.budget}.edgelist'
    bin = "all"
    # Load graph
    G = nx.read_edgelist(args.graph_path, nodetype=int)

    # Parse clusters.tab
    clusters_all = parse_clusters_tab(args.clusters_path)

    if bin == "all":
        clusters_bin = clusters_all
    else:
        # Pick only one bin, e.g. "[11-50]"
        clusters_bin = filter_bin(clusters_all, bin)


    print(f"Bin {bin} has", len(clusters_bin), "clusters")
    phi_before = min(c["phi"] for c in clusters_bin)    
    print("Before improvement, smallest phi in bin:", phi_before)


    # Improve them
    improved, stats = improve_bin(G, clusters_bin, budget=args.budget, only_fallback=args.only_fallback)

    print("After improvement, smallest phi in bin:", min(c["phi"] for c in improved))

    # Save new graph
    nx.write_edgelist(G, output_path, data=False)
    print("Wrote new graph to", output_path)


    print("Stricts edges added:", stats["strict_edges"])
    print("Fallback edges added:", stats["fallback_edges"])
    print("Total edges added:", stats["strict_edges"] + stats["fallback_edges"])

    phi_after = min(c["phi"] for c in improved)
    improvement = ((phi_after - phi_before) / phi_before) * 100 if phi_before != 0 else 0
    print(f"Percentage of improvement in smallest phi: {improvement:.2f}%")

if __name__ == "__main__":
    main()


# %%



