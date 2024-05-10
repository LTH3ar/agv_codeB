#!/bin/bash
# This script is used as wrapper for B_solver.py to redirect the output to a file
# Usage: ./B_solver.sh <input_file> <output_file>
echo "Running B_solver.py"
echo "Input file: $1"
echo "Output file: $2"
echo "Please wait..." # during this time, tee will write the output to the file
python B_solver_v2.py $1 | tee $2
echo "Done. Output written to $2"