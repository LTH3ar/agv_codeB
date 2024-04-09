from pyscipopt import Model, quicksum

"""
Khởi tạo các biến quyết định và ràng buộc cho bài toán
model: mô hình tối ưu hóa
vars_by_index_i: lưu trữ các biến theo chỉ số i
vars_by_index_j: lưu trữ các biến theo chỉ số j
vars_and_costs: lưu trữ chi phí của mỗi biến
exclude_i: lưu trữ các điểm i cần loại trừ(supply node)
exclude_j: lưu trữ các điểm j cần loại trừ(demand node)
arc_connect: lưu trữ các cung
zero_demand_supply: lưu trữ các điểm không có demand hay supply
edge_vars: lưu trữ capacity của mỗi cung
earliness_and_tardiness: lưu trữ earliness và tardiness
"""
model = Model("Simple linear optimization")
vars_by_index_i = {}
vars_by_index_j = {}
vars_and_costs = {}
# Khởi tạo tập hợp để theo dõi các điểm i và j cần loại trừ
exclude_i = set()
exclude_j = set()
# Huy: Khởi tạo tập hợp lưu trữ kết nối arc
arc_connect = []
# Huy: Khởi tạo tập hợp lưu trữ node không có demand hay supply
zero_demand_supply = set()
# Huy: Tạo một từ điển để lưu trữ biến cho mỗi cung
edge_vars = {} # format: {(src, dest): cap}
# Huy: Tạo một từ điển để lưu trữ tardiness và earliness
earliness_and_tardiness = {} # format: {node: (earliness, tardiness)}


"""
Đọc file và tạo biến quyết định
"""
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
            # Huy: Lưu trữ các cung không tự động sort vị trí của các biến
            arc_connect.append((i, j))
            for source in exclude_i:
                # Huy: Tạo biến quyết định x{source}_i_j, source là điểm xe xuất phát, i là điểm nguồn, j là điểm đích
                var_name = f"x{source}_{i}_{j}"
                model.addVar(vtype="B", name=var_name)

                vars_by_index_i.setdefault(i, []).append(var_name)
                vars_by_index_j.setdefault(j, []).append(var_name)
                vars_and_costs[var_name] = cij

                # Huy: Lưu trữ biến capacity cho mỗi cung
                edge_vars[(i, j)] = cap

                if i not in exclude_i and i not in exclude_j:
                    zero_demand_supply.add(i)

        # Huy: Thêm ràng buộc về earliness và tardiness đọc các dòng comment 'c' theo sau là 'tw'
        elif parts[0] == 'c':
            # Huy: kiểm tra xem có 'tw'
            if parts[1] == 'tw':
                earliness_and_tardiness[parts[2]] = (int(parts[3]), int(parts[4]))

"""
all_vars: lưu trữ tất cả các biến từ mô hình
var_dict: tạo một từ điển để liên kết tên biến với biến
"""
# Retrieve all variables from the model
all_vars = model.getVars()
# Create a dictionary to map variable names to variable objects
var_dict = {v.name: v for v in all_vars}


"""
cách tính toán ràng buộc:
- Sum các biến x{source}_i_j = 1 
- i là điểm nguồn bắt đầu của xe(node có supply) 
- j là điểm đích có liên kết với i theo cung hướng ra
vd: xe vị trí node 0 có đường ra đến node 3 và 11 -> x0_0_3 + x0_0_11 = 1
vd: xe vị trí node 3 có đường ra đến node 2 và 6 -> x3_3_2 + x3_3_6 = 1
"""
# Huy: Thêm ràng buộc hướng đi của xe
# Ràng buộc về điểm xuất phát của xe 0 và xe 3
for source in exclude_i:
    # tìm trong danh sách các biến có tên chứa source như x0_0_3, x3_0_3
    source_vars = [var for var in all_vars if f"x{source}_{source}" in var.name]
    # thêm ràng buộc để điểm xuất phát của xe 0 và xe 3
    model.addCons(quicksum(source_vars) == 1)


"""
cách tính toán ràng buộc:
- Sum các biến x{source}_i_j = 1
- j là điểm đích của xe (node có demand)
- i là điểm xuất phát có liên kết với j theo cung hướng vào
- bởi vì các xe có thể chọn một trong các điểm đích để đến, ta phải bao gồm tất cả source vào ràng buộc
vd: node 6 có đường vào từ node 3 và 8 và nhận cả 2 xe 0 và 3 -> x0_3_6 + x3_3_6 + x0_8_6 + x3_8_6 = 1
vd: node 9 có đường vào từ node 6 và 11 và nhận cả 2 xe 0 và 3 -> x0_6_9 + x3_6_9 + x0_11_9 + x3_11_9 = 1
"""
# Thêm ràng buộc: tổng tất cả các xji = 1 với mỗi j có giá trị '-1'
for j, var_names in vars_by_index_j.items():
    if j in exclude_j:
        model.addCons(quicksum(var_dict[name] for name in var_names if name in var_dict) == 1)


"""
cách tính toán ràng buộc:
- Sum các biến x{source}_i_j <= 1
- i là đi, j là điểm đến
- cung có capacity
- bởi vì mỗi cung chỉ có thể đi qua 1 xe nên tổng số xe đi qua cung đó không vượt quá capacity(capacity được định trong file input)
vd: cung từ node 0 đến node 3 có capacity là 1 -> x0_0_3 + x3_0_3 <= 1
vd: cung từ node 3 đến node 6 có capacity là 1 -> x0_3_6 + x3_3_6 <= 1
"""
# Huy: Thêm ràng buộc để đảm bảo rằng tổng số xe di chuyển trên mỗi cung không vượt quá giới hạn cho phép
# kiểm tra trong edge_vars, nếu i, j có trong edge_vars thì thêm ràng buộc
for (i, j), cap in edge_vars.items():
    if i in vars_by_index_i and j in vars_by_index_j:
        sum_ij = quicksum(var_dict[name] for name in vars_by_index_i[i] if name in vars_by_index_j[j] and name in var_dict)
        model.addCons(sum_ij <= cap)


# Huy: Ràng buộc về liên thông
# Add constraints to the model
"""
cách tính toán ràng buộc:
- phần này phụ thuộc vào cách đọc file và cách tạo biến quyết định
- file đầu vào phải được đọc theo thứ tự từ trên xuống dưới và các dòng dữ liệu phải được sắp xếp theo thứ tự
- chỉ đơn thuần so sánh các luồng đi bằng cách chia cặp các arc theo thứ tự như file dimacs
(x0_3_2 == x0_2_0)
(x3_3_2 == x3_2_0)

(x0_6_5 == x0_5_3)
(x3_6_5 == x3_5_3)

(x0_9_8 == x0_8_6)
(x3_9_8 == x3_8_6)

(x0_0_11 == x0_11_9)
(x3_0_11 == x3_11_9)

dimacs:
a 0 11 0 1 2
a 11 9 0 1 2

a 9 8 0 1 2
a 8 6 0 1 2

a 6 5 0 1 2
a 5 3 0 1 2

a 3 2 0 1 2
a 2 0 0 1 2
"""
"""
# Phụ thuộc quá nhiều vào cách đọc file và cách tạo biến quyết định
# Chỉnh các ràng buộc sang tự động dựa theo arc_connect và source
counter = 0
while counter < len(arc_connect):
    i, j = arc_connect[counter]
    i_next, j_next = arc_connect[counter + 1]
    # check if both i, j either belong to zero_demand_supply
    if i in zero_demand_supply or j in zero_demand_supply:
        for source in exclude_i:
            var_name = f"x{source}_{i}_{j}"
            var_next_name = f"x{source}_{i_next}_{j_next}"
            if var_name in var_dict and var_next_name in var_dict:
                model.addCons(var_dict[var_name] == var_dict[var_next_name])

    if counter + 3 < len(arc_connect):
        counter += 2
    else:
        break
"""
# Huy: Chỉnh các ràng buộc sang tự động
# Huy: Chỉnh các ràng buộc sang tự động
# tạo dict theo từng node không có demand để lưu trữ các biến arc của node đó
# lưu format: {node: [arc1, arc2,...} với các giá trị arc thuộc arc_connect
zero_demand_supply_node_dict = {}
for node in zero_demand_supply:
    for arc_i, arc_j in arc_connect:
        if arc_i == node:
            # append both arc_i, arc_j to the list
            zero_demand_supply_node_dict.setdefault(node, []).append((arc_i, arc_j))
        elif arc_j == node:
            # append both arc_i, arc_j to the list
            zero_demand_supply_node_dict.setdefault(node, []).append((arc_i, arc_j))

for source in exclude_i:
    for node, arcs in zero_demand_supply_node_dict.items():
        model.addCons(var_dict[f"x{source}_{arcs[0][0]}_{arcs[0][1]}"] == var_dict[f"x{source}_{arcs[1][0]}_{arcs[1][1]}"])




"""
#hard code
# ràng buộc về liên thông cho điểm nguồn
model.addCons(var_dict['x0_0_11'] + var_dict['x0_0_3'] == 1 + var_dict['x0_2_0'] + var_dict['x0_9_0'])
model.addCons(var_dict['x0_3_2'] + var_dict['x0_3_6'] == var_dict['x0_0_3'] + var_dict['x0_5_3'])

model.addCons(var_dict['x3_0_11'] + var_dict['x3_0_3'] == var_dict['x3_2_0'] + var_dict['x3_9_0'])
model.addCons(var_dict['x3_3_2'] + var_dict['x3_3_6'] == 1 + var_dict['x3_0_3'] + var_dict['x3_5_3'])
"""
"""
cách tính toán ràng buộc:
- phân chia các biến đại diện cho các arc thành 2 loại: inbound và outbound
- inbound: các biến có dạng x{source}_i_j với j là node có supply
- outbound: các biến có dạng x{source}_i_j với i là node có supply
- sau đó thêm ràng buộc tổng các biến inbound + 1 = tổng các biến outbound(cho mỗi xe)
"""
# Huy: Chỉnh các ràng buộc sang tự động
"""
các điểm nguồn sẽ có 2 inbound và 2 outbound
vd: 0 sẽ đi đến 3 hoặc 11, và 2, 9 sẽ đi đến 0
vd: 3 sẽ đi đến 2 hoặc 6, và 0, 5 sẽ đi đến 3 

outbound format: x{source}_{i}_{j} với i là một trong các điểm nguồn, có 2 xe
vd: x0_0_3 và x3_0_3

inbound format: x{source}_{i}_{j} với j là một trong các điểm nguồn, có 2 xe
vd: x0_2_0 và x3_2_0
"""
src_outbound_arc = {}
src_inbound_arc = {}
for source in exclude_i:
    src_outbound_arc[source] = [var for var in all_vars if f"_{source}_" in var.name]
    src_inbound_arc[source] = [var for var in all_vars if var.name[-1] == source]
"""
output of outbound_arc and inbound_arc
outbound: {'3': [x3_3_6, x0_3_6, x3_3_2, x0_3_2], '0': [x3_0_3, x0_0_3, x3_0_11, x0_0_11]}
inbound: {'3': [x3_0_3, x0_0_3, x3_5_3, x0_5_3], '0': [x3_9_0, x0_9_0, x3_2_0, x0_2_0]}
"""
# Huy: dựa vào outbound và inbound để thêm ràng buộc
for source in exclude_i:
    for var in src_outbound_arc[source]:
        out_sum = quicksum(src_outbound_arc[source])
    for var in src_inbound_arc[source]:
        in_sum = 1 + quicksum(src_inbound_arc[source])
    model.addCons(out_sum == in_sum)





"""
#hard code
# ràng buộc về liên thông cho điểm đích
model.addCons(var_dict['x0_11_9'] + var_dict['x3_11_9'] + var_dict['x0_6_9'] + var_dict['x3_6_9'] == 1 + var_dict['x0_9_8'] + var_dict['x3_9_8'] + var_dict['x0_9_0'] + var_dict['x3_9_0'])
model.addCons(var_dict['x0_6_9'] + var_dict['x3_6_9'] + var_dict['x0_6_5'] + var_dict['x3_6_5'] + 1 == var_dict['x0_3_6'] + var_dict['x3_3_6'] + var_dict['x0_8_6'] + var_dict['x3_8_6'])
"""
"""
cách tính toán ràng buộc:
- phân chia các biến đại diện cho các arc thành 2 loại: inbound và outbound
- inbound: các biến có dạng x{source}_i_j với j là node có demand
- outbound: các biến có dạng x{source}_i_j với i là node có demand
- sau đó thêm ràng buộc tổng các biến inbound = tổng các biến outbound + 1(cho mỗi xe)
"""
# Huy: Chỉnh các ràng buộc sang tự động
dest_outbound_arc = {}
dest_inbound_arc = {}
for dest in exclude_j:
    dest_outbound_arc[dest] = [var for var in all_vars if f"_{dest}_" in var.name]
    dest_inbound_arc[dest] = [var for var in all_vars if var.name[-1] == dest]

for dest in exclude_j:
    for var in dest_outbound_arc[dest]:
        out_sum = 1 + quicksum(dest_outbound_arc[dest])
    for var in dest_inbound_arc[dest]:
        in_sum = quicksum(dest_inbound_arc[dest])
    model.addCons(out_sum == in_sum)




"""
cách tính toán ràng buộc:
- tính chi phí tối ưu
- tạo biến z{source} để lưu trữ chi phí tối ưu
"""
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

    model.addCons(z_var_tw_t >= (z_var - tardiness) * vars_sum)
    model.addCons(z_var_tw_e >= (earliness * vars_sum) - z_var)
    model.addCons(z_var_tw_e >= 0)
    model.addCons(z_var_tw_t >= 0)




# Huy: Tính chi phí tối ưu
alpha = 1
beta = 1
# Huy: Tính chi phí tối ưu
# alpha with z_vars
alpha_sum = quicksum(alpha * z_var for z_var in z_vars.values())
# beta with z_vars_tw
beta_sum = quicksum(beta * z_var_tw for (_, _), (z_var_tw_e, z_var_tw_t) in z_vars_tw.items() for z_var_tw in (z_var_tw_e, z_var_tw_t))
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

