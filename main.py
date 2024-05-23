from agv_module import agv_solver

file_reader = agv_solver.FileReader("/home/raven/git_repo/github/agv_codeB/input_dimacs/supply_03_demand_69.txt")
file_reader.read_custom_dimacs()
problem_info, supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict = file_reader.get_all_dicts()

model = agv_solver.MinimumCostFlowModel(supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict)
model.solve()
solution = model.get_solution_dict()
print(solution)
model.output_solution()