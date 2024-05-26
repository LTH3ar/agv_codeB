from forecasting_model_module.ForecastingModel import ForecastingModel, DimacsFileReader

file_reader = DimacsFileReader("input_dimacs/supply_03_demand_69.txt")
file_reader.read_custom_dimacs()
problem_info, supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict = file_reader.get_all_dicts()
model = ForecastingModel(problem_info, supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict)
model.solve()
model.output_solution()
model.save_solution("supply_03_demand_69_edit.txt", "ForecastingModuleTestOutput")
model.create_traces("traces.txt")