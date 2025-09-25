#!/bin/bash
# Usage: ./run_ncp.sh <input_graph> <output_file>
NCP_EXEC="../snap/examples/Release/ncpplot"
INPUT="$1"
OUTPUT="$2"

$NCP_EXEC -i:$INPUT -k -s -topn:1 -o:$OUTPUT
