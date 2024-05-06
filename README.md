# agv_codeB

## File Structure

1. File:
   - `A.py` - Hardcoded version of the code for supply 03 demand 69
   - `B_details.py` - old version of the code with dynamic constraints
   - `B_solver.py` - new version of the code with dynamic constraints and OOP structure
   - `B_solver.sh` - shell script wrapper to run the code

2. Directory:
    - `input_dimacs` - contains DIMACS format input files
    - `output_B_solver` - contains output files generated by `B_solver.py`
    - `old_files` - contains old files
    - `old_output` - contains old output files

## How to run the code

- Add executable permission to `B_solver.sh` by running `chmod +x B_solver.sh`
- Run the code by running `./B_solver.sh <input_file> <output_file>` where `<input_file>` is the input file in DIMACS format and `<output_file>` is the output file where the solution will be written.
- Example: `./B_solver.sh input_dimacs/instance_03_69_01.dimacs output_B_solver/instance_03_69_01.out`