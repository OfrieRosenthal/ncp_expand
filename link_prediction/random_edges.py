#!/usr/bin/env python3
import argparse
import networkx as nx
import random
import os


def add_random_edges_probabilistic(G, K, seed=None, max_attempts=None):
    """
    Adds K random non-existing edges to G using a probabilistic method.
    Memory-efficient for very large graphs.
    """
    if seed is not None:
        random.seed(seed)

    if max_attempts is None:
        max_attempts = 100 * K

    nodes = list(G.nodes())
    added_edges = set()
    attempts = 0

    while len(added_edges) < K and attempts < max_attempts:
        u, v = random.sample(nodes, 2)
        if not G.has_edge(u, v) and (u, v) not in added_edges and (v, u) not in added_edges:
            added_edges.add((u, v))
        attempts += 1

    if len(added_edges) < K:
        print(f"⚠️ Warning: Only added {len(added_edges)} edges out of {K} requested.")

    G.add_edges_from(added_edges)

    # Safety check
    assert len(added_edges) <= K, (
        f"Error: added {len(added_edges)} edges, "
        f"but only {K} were requested."
    )

    return G, list(added_edges)


def main():
    parser = argparse.ArgumentParser(description="Add random edges to a graph and save the result.")
    parser.add_argument("--graph", type=str,
                        default="../datasets/facebook/facebook_combined.txt",
                        help="Path to input edgelist file (default: ../datasets/facebook/facebook_combined.txt)")
    parser.add_argument("--output", type=str,
                        help="Path to output edgelist file. "
                             "If not provided, defaults to '../target/random/facebook_random_{K}.edgelist'")
    parser.add_argument("-K", type=int, default=200,
                        help="Number of edges to add (default: 200)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")

    args = parser.parse_args()

    # If no output given, generate one automatically under ../target/random/
    if args.output is None:
        target_dir = "../target/random"
        os.makedirs(target_dir, exist_ok=True)
        args.output = os.path.join(target_dir, f"facebook_random_{args.K}.edgelist")

    # Load graph
    print(f"📂 Reading graph from {args.graph} ...")
    G = nx.read_edgelist(args.graph, nodetype=int)

    # Add random edges
    G, added_edges = add_random_edges_probabilistic(G, K=args.K, seed=None)
    print(f"✅ Added {len(added_edges)} edges")

    # Save updated graph
    nx.write_edgelist(G, args.output, data=False)
    print(f"💾 Graph saved to {args.output}")

    # Check for duplicates in file
    edges = []
    with open(args.output, "r") as f:
        for line in f:
            u, v = line.strip().split()
            edges.append(tuple(sorted((u, v))))

    print("📊 Total edges in file:", len(edges))
    if len(edges) != len(set(edges)):
        print("⚠️ The file has duplicate edges!")



if __name__ == "__main__":
    main()
