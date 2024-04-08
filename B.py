from pyscipopt import Model, quicksum

model = Model("Simple linear optimization")
vars_by_index_i = {}
vars_by_index_j = {}
vars_and_costs = {}
# Khởi tạo tập hợp để theo dõi các điểm i và j cần loại trừ
exclude_i = set()
exclude_j = set()

# Huy: Khởi tạo tập hợp lưu trữ nguồn các xe đi từ điểm nguồn
zero_demand_nodes = set() # format: {node} # lưu trữ các điểm có demand = 0 (lấy từ trong arc)

# Huy: Tạo một từ điển để lưu trữ biến cho mỗi cung
edge_vars = {} # format: {(src, dest): cap}

# Huy: Tạo một từ điển để lưu trữ tardiness và earliness
earliness_and_tardiness = {} # format: {node: (earliness, tardiness)}

# 2 route
# 1. 0 -> 3 -> 6 -> 9 -> 0
# 2. 0 -> 11 -> 9 -> 8 -> 6 -> 5 -> 3 -> 2 -> 0

# Đọc file và tạo biến quyết định
with open('simpleInput2.txt', 'r') as file:
    for line in file:
        parts = line.strip().split()
        if parts[0] == 'n':
            # Lưu trữ chỉ số i hoặc j để sau này thêm ràng buộc
            index = parts[1]
            if parts[2] == '1':
                exclude_i.add(parts[1])
                vars_by_index_i.setdefault(index, [])
                # Lưu trữ các điểm nguồn
            elif parts[2] == '-1':
                exclude_j.add(parts[1])
                vars_by_index_j.setdefault(index, [])

        elif parts[0] == 'a':
            # i là điểm nguồn, j là điểm đích, cij là chi phí
            i, j, cap, cij = parts[1], parts[2], int(parts[4]), int(parts[5])
            if i not in exclude_i and i not in exclude_j:
                zero_demand_nodes.add(i)
            for source in exclude_i:
                # Huy: Tạo biến quyết định x{source}_i_j, source là điểm xe xuất phát, i là điểm nguồn, j là điểm đích
                var_name = f"x{source}_{i}_{j}"
                model.addVar(vtype="B", name=var_name)

                vars_by_index_i.setdefault(i, []).append(var_name)
                vars_by_index_j.setdefault(j, []).append(var_name)
                vars_and_costs[var_name] = cij

                # Huy: Lưu trữ biến capacity cho mỗi cung
                edge_vars[(i, j)] = cap

        elif parts[0] == 'c':
            # Huy: kiểm tra xem có 'tw'
            if parts[1] == 'tw':
                earliness_and_tardiness[parts[2]] = (int(parts[3]), int(parts[4]))


# Retrieve all variables from the model
all_vars = model.getVars()
# Create a dictionary to map variable names to variable objects
var_dict = {v.name: v for v in all_vars}


# Huy: Thêm ràng buộc hướng đi của xe
# Ràng buộc về điểm xuất phát của xe 0 và xe 3
for source in exclude_i:
    # tìm trong danh sách các biến có tên chứa source như x0_0_3, x3_0_3
    source_vars = [var for var in all_vars if f"x{source}_{source}" in var.name]
    print(f"source_vars: {source_vars}")
    # thêm ràng buộc để điểm xuất phát của xe 0 và xe 3
    model.addCons(quicksum(source_vars) == 1)

# Thêm ràng buộc: tổng tất cả các xji = 1 với mỗi j có giá trị '-1'
for j, var_names in vars_by_index_j.items():
    if j in exclude_j:
        model.addCons(quicksum(var_dict[name] for name in var_names if name in var_dict) == 1)

# Huy: Thêm ràng buộc để đảm bảo rằng tổng số xe di chuyển trên mỗi cung không vượt quá giới hạn cho phép
# kiểm tra trong edge_vars, nếu i, j có trong edge_vars thì thêm ràng buộc
for (i, j), cap in edge_vars.items():
    if i in vars_by_index_i and j in vars_by_index_j:
        sum_ij = quicksum(var_dict[name] for name in vars_by_index_i[i] if name in vars_by_index_j[j] and name in var_dict)
        model.addCons(sum_ij <= cap)

# Thêm ràng buộc: tổng tất cả các xij = tổng tất cả các xjk cho mỗi j
for j in vars_by_index_j.keys():
	if j in vars_by_index_i and j not in exclude_i and j not in exclude_j:
		#model.addCons(quicksum(model.getVarByName(name) for name in vars_by_index_i[j]) == quicksum(model.getVarByName(name) for name in vars_by_index_j[j]))
		sum_i = quicksum(var_dict[name] for name in vars_by_index_i[j] if name in var_dict)
		sum_j = quicksum(var_dict[name] for name in vars_by_index_j[j] if name in var_dict)
		model.addCons(sum_i == sum_j)


# Huy: Tạo z{source}(z0, z3) để lưu trữ chi phí tối ưu
z_vars = {}
for source in exclude_i:
    z_var_name = f"z{source}"
    z_vars[source] = model.addVar(vtype="I", name=z_var_name)

# Huy: Thêm ràng buộc để tính chi phí tối ưu
for source in exclude_i:
    z_var = z_vars[source]
    #print(f"{source} = {z_var}")
    # tìm trong danh sách các biến có tên chứa source như x0_0_3, x3_0_3
    source_vars = [var for var in all_vars if f"x{source}_" in var.name]
    #print(source_vars)
    # thêm ràng buộc để tính chi phí tối ưu
    # model.addCons(z_var == tổng(chi phí của các biến * giá trị của biến đi(x{source}_i_j)))
    model.addCons(z_var == quicksum(vars_and_costs[var.name] * var_dict[var.name] for var in source_vars if var.name in var_dict))


# Huy: Thêm ràng buộc để tính earliness và tardiness
z_vars_tw = {}
for source in exclude_i:
    for dest in exclude_j:
        z_var_tw_e = model.addVar(vtype="C", name=f"z{source}TW{dest}E")
        z_var_tw_t = model.addVar(vtype="C", name=f"z{source}TW{dest}T")
        z_vars_tw[(source, dest)] = (z_var_tw_e, z_var_tw_t)


for (source, dest), (z_var_tw_e, z_var_tw_t) in z_vars_tw.items():
    z_var = z_vars[source]
    # tìm trong danh sách các biến có tên chứa x{source)_i_{dest} như x0_3_6, x0_8_6
    z_vars_src_dest = {}
    for var in all_vars:
        if (f"x{source}" in var.name) and (var.name[-1] == dest):
            z_vars_src_dest[var.name] = var

    # tìm gía trị của tardiness và earliness
    earliness, tardiness = earliness_and_tardiness[dest]
    #print(earliness, tardiness)

    # thêm ràng buộc để tính earliness và tardiness
    vars_sum = quicksum(z_vars_src_dest.values())
    #print(vars_sum)

    model.addCons(z_var_tw_t >= (z_var - tardiness) * vars_sum)
    model.addCons(z_var_tw_e >= (earliness * vars_sum) - z_var)
    model.addCons(z_var_tw_e >= 0)
    model.addCons(z_var_tw_t >= 0)


# Tối ưu hóa mô hình
#model.setObjective(quicksum(vars_and_costs[var_name] * var_dict[var_name] for var_name in vars_and_costs), "minimize")

# Huy: Tính chi phí tối ưu
alpha = 1
beta = 1
# Huy: Tính chi phí tối ưu
# alpha with z_vars
alpha_sum = quicksum(alpha * z_var for z_var in z_vars.values())
print(alpha_sum)
# beta with z_vars_tw
beta_sum = quicksum(beta * z_var_tw for (_, _), (z_var_tw_e, z_var_tw_t) in z_vars_tw.items() for z_var_tw in (z_var_tw_e, z_var_tw_t))
print(beta_sum)
model.setObjective(alpha_sum + beta_sum, "minimize")


model.optimize()
if model.getStatus() == "optimal":
    print("Optimal value:", model.getObjVal())
    print("Solution:")
    # Lấy tất cả các biến từ mô hình
    vars = model.getVars()
    # In giá trị của tất cả các biến
    for var in vars:
        if model.getVal(var) > 0:
            print(f"{var.name} = {model.getVal(var)}")
else:
    print("Không tìm thấy giải pháp tối ưu.")

