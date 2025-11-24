#!/usr/bin/env python3
import argparse
import subprocess
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Driver for worst_ncp.py and random_edges.py experiments")
    parser.add_argument(
        "--budgets", type=int, nargs="+", required=True,
        help="List of budgets (e.g. --budgets 50 100 200)"
    )
    parser.add_argument(
        "--graph_path", type=str,
        default="../datasets/facebook/facebook_combined.txt",
        help="Path to input graph"
    )
    parser.add_argument(
        "--clusters_path", type=str,
        default="../datasets/facebook/ncp_original_graph/ncp.facebook_combined.perbin.clusters.tab",
        help="Path to clusters.tab file"
    )
    parser.add_argument(
        "--worst_script", type=str, default="worst_ncp.py",
        help="Path to worst_ncp.py script"
    )
    parser.add_argument(
        "--random_script", type=str, default="random_edges.py",
        help="Path to random_edges.py script"
    )
    return parser.parse_args()

def run_worst_ncp(script_path, graph_path, clusters_path, budget, fallback=False):
    cmd = [
        "python", script_path,
        "--graph_path", graph_path,
        "--clusters_path", clusters_path,
        "--budget", str(budget)
    ]
    mode = "fallback" if fallback else "strict"
    if fallback:
        cmd.append("--only_fallback")
    
    print(f"\nRunning worst_ncp.py {mode} (budget={budget})...")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    output = result.stdout

    # Extract stats from printed output
    strict_edges = int(re.search(r"Stricts edges added:\s*(\d+)", output).group(1))
    fallback_edges = int(re.search(r"Fallback edges added:\s*(\d+)", output).group(1))
    total_edges = int(re.search(r"Total edges added:\s*(\d+)", output).group(1))
    improvement = float(re.search(r"Percentage of improvement in smallest phi:\s*([0-9.]+)%", output).group(1))

    return {
        "budget": budget,
        "mode": mode,
        "strict_edges": strict_edges,
        "fallback_edges": fallback_edges,
        "total_edges": total_edges,
        "improvement": improvement
    }

def run_random_edges(script_path, graph_path, budget):
    cmd = [
        "python", script_path,
        "--graph", graph_path,
        "-K", str(budget)
    ]
    print(f"\nRunning random_edges.py (budget={budget})...")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    output = result.stdout

    edges_added = int(re.search(r"✅ Added (\d+) edges", output).group(1))
    return {"budget": budget, "edges_added": edges_added}

def main():
    args = parse_args()
    summary = []

    for budget in args.budgets:
        # Strict run
        strict_stats = run_worst_ncp(args.worst_script, args.graph_path, args.clusters_path, budget, fallback=False)
        summary.append(strict_stats)

        # Fallback run
        fallback_stats = run_worst_ncp(args.worst_script, args.graph_path, args.clusters_path, budget, fallback=True)
        summary.append(fallback_stats)

        # Random run
        random_stats = run_random_edges(args.random_script, args.graph_path, budget)
        summary.append({
            "budget": budget,
            "mode": "random",
            "edges_added": random_stats["edges_added"]
        })

    # Print summary
    print("\n=== Summary of all runs ===")
    print(f"{'Budget':>6} | {'Mode':>8} | {'Strict':>6} | {'Fallback':>8} | {'Total':>6} | {'Improvement %':>14} | {'Random edges':>12}")
    print("-"*80)
    for row in summary:
        if row["mode"] == "random":
            print(f"{row['budget']:>6} | {row['mode']:>8} | {'-':>6} | {'-':>8} | {'-':>6} | {'-':>14} | {row['edges_added']:>12}")
        else:
            print(f"{row['budget']:>6} | {row['mode']:>8} | {row['strict_edges']:>6} | {row['fallback_edges']:>8} | {row['total_edges']:>6} | {row['improvement']:>14.2f} | {'-':>12}")

if __name__ == "__main__":
    main()
