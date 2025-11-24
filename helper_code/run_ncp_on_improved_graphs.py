#!/usr/bin/env python3
import argparse
import os
import subprocess

def run_ncp(input_file, out_dir, ncpplot_path, method, budget, created_dirs):
    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

    file_name = os.path.basename(input_file)
    input_file_abs = os.path.abspath(input_file)
    ncpplot_abs = os.path.abspath(ncpplot_path)

    print("\n" + "#"*75)
    print(f"RUNNING NCP: method={method.upper()} | budget={budget} | file={file_name}")
    print("#"*75 + "\n")

    cmd = [
        ncpplot_abs,
        f"-i:{input_file_abs}",
        "-k",
        "-s",
        "-topn:250"
        # -o removed
    ]

    try:
        # run ncpplot with cwd set to out_dir
        subprocess.run(cmd, check=True, cwd=out_dir)
        print(f"✅ NCP output should be in: {out_dir}\n")
        created_dirs.append(out_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running ncpplot on {input_file}")
        print(f"Command {cmd} died with {e}\n")
    except FileNotFoundError:
        print(f"❌ ncpplot executable not found at {ncpplot_abs}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--budgets", type=int, nargs="+", required=True)
    parser.add_argument("--wncp_strict_folder", type=str, default="../target/wncp/strict")
    parser.add_argument("--wncp_fallback_folder", type=str, default="../target/wncp/fallback")
    parser.add_argument("--random_folder", type=str, default="../target/random")
    parser.add_argument(
        "--ncpplot_path",
        type=str,
        default="../snap/examples/Release/ncpplot",
        help="Path to the ncpplot executable"
    )
    parser.add_argument("--dataset_name", type=str, default="facebook")
    args = parser.parse_args()

    created_dirs = []

    for budget in args.budgets:
        # Strict
        strict_path = os.path.join(args.wncp_strict_folder, f"{args.dataset_name}_wncp_{budget}.edgelist")
        strict_out_dir = os.path.join("../target/ncp_plots", args.dataset_name, "strict")
        run_ncp(strict_path, strict_out_dir, args.ncpplot_path, method="strict", budget=budget, created_dirs=created_dirs)

        # Fallback
        fallback_path = os.path.join(args.wncp_fallback_folder, f"{args.dataset_name}_fallback_wncp_{budget}.edgelist")
        fallback_out_dir = os.path.join("../target/ncp_plots", args.dataset_name, "fallback")
        run_ncp(fallback_path, fallback_out_dir, args.ncpplot_path, method="fallback", budget=budget, created_dirs=created_dirs)

        # Random
        random_path = os.path.join(args.random_folder, f"{args.dataset_name}_random_{budget}.edgelist")
        random_out_dir = os.path.join("../target/ncp_plots", args.dataset_name, "random")
        run_ncp(random_path, random_out_dir, args.ncpplot_path, method="random", budget=budget, created_dirs=created_dirs)

    print("\n" + "="*60)
    print("✅ NCP processing complete. Output directories created:")
    for d in created_dirs:
        print(d)
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
