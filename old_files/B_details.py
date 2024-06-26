from pyscipopt import Model, quicksum

"""
Khởi tạo các biến quyết định và ràng buộc cho bài toán
model: mô hình tối ưu hóa
vars_by_index_i: lưu trữ các biến theo chỉ số i {'i': ['x0_i_j', 'x3_i_j', ...], 'i': ['x0_i_j', 'x3_i_j', ...], ...}
vars_by_index_j: lưu trữ các biến theo chỉ số j {'j': ['x0_i_j', 'x3_i_j', ...], 'j': ['x0_i_j', 'x3_i_j', ...], ...}
vars_and_costs: lưu trữ chi phí của mỗi biến {'x0_i_j': cij, 'x3_i_j': cij, ...}
exclude_i: lưu trữ các điểm i cần loại trừ(supply node) ['0', '3', ...]
exclude_j: lưu trữ các điểm j cần loại trừ(demand node) ['6', '9', ...]
arc_connect: lưu trữ các cung [(i, j), (i, j), ...]
zero_demand_supply: lưu trữ các điểm không có demand hay supply ['2', '5', ...]
edge_vars: lưu trữ capacity của mỗi cung {(src, dest): cap, (src, dest): cap, ...}
earliness_and_tardiness: lưu trữ earliness và tardiness của mỗi node {'node': (earliness, tardiness), 'node': (earliness, tardiness), ...}
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
with open('dimacs.min', 'r') as file:
    for line in file:
        # split delimeter ' ' để lấy các phần tử trong dòng
        parts = line.strip().split(' ')
        if parts[0] == 'n':
            # Lưu trữ chỉ số i hoặc j để sau này thêm ràng buộc
            index = parts[1]
            if int(parts[2]) > 0:
                exclude_i.add(parts[1])
                vars_by_index_i.setdefault(index, [])
                # Lưu trữ các điểm nguồn
            elif int(parts[2]) < 0:
                exclude_j.add(parts[1])
                vars_by_index_j.setdefault(index, [])

        elif parts[0] == 'a':
            # i là điểm nguồn, j là điểm đích, cij là chi phí
            i, j, cap, cij = parts[1], parts[2], int(parts[4]), int(parts[5])
            #i, j, cap, cij = parts[1], parts[2], int(1), int(parts[3])
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

                if (i not in exclude_i) and (i not in exclude_j) and (i not in zero_demand_supply):
                    zero_demand_supply.add(i)

        # Huy: Thêm ràng buộc về earliness và tardiness đọc các dòng comment 'c' theo sau là 'tw'
        elif parts[0] == 'c':
            # Huy: kiểm tra xem có 'tw'
            if len(parts) > 1 and parts[1] == 'tw':
                earliness_and_tardiness[parts[2]] = (int(parts[3]), int(parts[4]))

"""
all_vars: lưu trữ tất cả các biến từ mô hình [x0_0_3, x3_0_3, x0_0_11, x3_0_11, ...]
var_dict: tạo một từ điển để liên kết tên biến với biến {'name': var, 'name': var, ...}
"""
# Retrieve all variables from the model
all_vars = model.getVars()
# Create a dictionary to map variable names to variable objects
var_dict = {v.name: v for v in all_vars}

# sort all the dict and set using integer value
exclude_i = sorted(exclude_i, key=lambda x: int(x))
exclude_j = sorted(exclude_j, key=lambda x: int(x))
arc_connect = sorted(arc_connect, key=lambda x: (int(x[0]), int(x[1])))
zero_demand_supply = sorted(zero_demand_supply, key=lambda x: int(x))
earliness_and_tardiness = dict(sorted(earliness_and_tardiness.items(), key=lambda x: int(x[0])))
vars_by_index_i = dict(sorted(vars_by_index_i.items(), key=lambda x: int(x[0])))
vars_by_index_j = dict(sorted(vars_by_index_j.items(), key=lambda x: int(x[0])))
edge_vars = dict(sorted(edge_vars.items(), key=lambda x: (int(x[0][0]), int(x[0][1]))))

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
        model.addCons(quicksum(var_dict[name] for name in var_names if name in var_dict) <= 1)


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
        #print(f"sum_ij: {sum_ij}")
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
# Huy: Chỉnh các ràng buộc sang tự động
# Huy: Chỉnh các ràng buộc sang tự động
# tạo dict theo từng node không có demand để lưu trữ các biến arc của node đó
# lưu format: {node: [arc1, arc2,...} với các giá trị arc thuộc arc_connect

# sort by node integer value
print(zero_demand_supply)

zero_demand_supply_node_dict_in = {}
zero_demand_supply_node_dict_out = {}
for node in zero_demand_supply:
    for arc_i, arc_j in arc_connect:
        if arc_i == node:
            # append both arc_i, arc_j to the list
            print(f"arc_i--> PUSH: {arc_i}, arc_j: {arc_j}")
            zero_demand_supply_node_dict_out.setdefault(node, []).append((arc_i, arc_j))
            print(f"arc_i--> DONE: {arc_i}, arc_j: {arc_j}")

        elif arc_j == node:
            # append both arc_i, arc_j to the list
            print(f"arc_j--> PUSH: {arc_i}, arc_j: {arc_j}")
            zero_demand_supply_node_dict_in.setdefault(node, []).append((arc_i, arc_j))
            print(f"arc_j--> DONE: {arc_i}, arc_j: {arc_j}")


#sort by node integer value
zero_demand_supply_node_dict_in = dict(sorted(zero_demand_supply_node_dict_in.items(), key=lambda x: int(x[0])))
zero_demand_supply_node_dict_out = dict(sorted(zero_demand_supply_node_dict_out.items(), key=lambda x: int(x[0])))
print(zero_demand_supply_node_dict_in)
print(zero_demand_supply_node_dict_out)

"""
Dựa theo yêu cầu của ràng buộc thì có 3 hướng implement:
"""

"""
Tính toán ràng buộc cho các điểm không có demand:
- Tổng đầu vào cả 2 xe bằng tổng đầu ra cả 2 xe:
    x0_3_2 + x3_3_2 + x0... + x3... = x0_2_0 + x3_2_0 + x0... + x3...
    
- Kết quả cho supply_03_demand_69.txt:
    Optimal value: 14.0
    Solution:
    x3_3_6 = 1.0
    x0_0_11 = 1.0
    x3_11_9 = 1.0
    z0 = 2.0
    z3 = 6.0
    z3TW6E = 1.0
    z3TW9E = 5.0
    
- Kết quả ra 368 for optimal cost (chỉ chạy đơn) cho 255 nodes:
    Optimal value: 368.0
    Solution:
    x24_23_13 = 1.0
    x24_22_23 = 1.0
    x2_2_22 = 1.0
    x2_36_37 = 1.0
    x24_37_38 = 1.0
    x24_38_39 = 1.0
    x2_39_40 = 1.0
    x2_116_117 = 1.0
    x2_138_128 = 1.0
    x2_128_129 = 1.0
    x24_129_130 = 1.0
    x24_130_131 = 1.0
    x24_137_138 = 1.0
    x2_117_137 = 1.0
    x24_24_47 = 1.0
    x24_47_70 = 1.0
    x24_70_93 = 1.0
    x2_93_116 = 1.0
    x2_13_36 = 1.0
    x24_131_254 = 1.0
    x24_40_255 = 1.0
"""
print("\n Method 1\n")
for node in zero_demand_supply:
    arcs_dict_in = zero_demand_supply_node_dict_in.get(node, [])
    arcs_dict_out = zero_demand_supply_node_dict_out.get(node, [])
    sum_arc_in = quicksum(var_dict[f"x{source}_{i}_{j}"] for source in exclude_i for i, j in arcs_dict_in)
    print(f"Sum arc in: {sum_arc_in}")
    sum_arc_out = quicksum(var_dict[f"x{source}_{i}_{j}"] for source in exclude_i for i, j in arcs_dict_out)
    print(f"Sum arc out: {sum_arc_out}")
    model.addCons(sum_arc_in == sum_arc_out)

# print("\n Method 2\n")
# for source in exclude_i:
#     for node in zero_demand_supply:
#         arcs_dict_in = zero_demand_supply_node_dict_in.get(node, [])
#         arcs_dict_out = zero_demand_supply_node_dict_out.get(node, [])
#         sum_arc_in = quicksum(var_dict[f"x{source}_{i}_{j}"] for i, j in arcs_dict_in)
#         sum_arc_out = quicksum(var_dict[f"x{source}_{i}_{j}"] for i, j in arcs_dict_out)
#         print(f"Sum arc in: {sum_arc_in}")
#         print(f"Sum arc out: {sum_arc_out}")
#         model.addCons(sum_arc_in == sum_arc_out)

# """
# Phương pháp tính toán ràng buộc ràng buộc khác:
# - Tổng đầu vào mỗi xe bằng tổng đầu ra mỗi xe:
#     x0_3_2 + x0_3_6 + x0... = x0_0_3 + x0_0_11 + x0...
#     x3_3_2 + x3_3_6 + x3... = x3_0_3 + x3_0_11 + x3...
# - Kết quả cho supply_03_demand_69.txt:
#     Optimal value: 18.0
#     Solution:
#     x3_3_6 = 1.0
#     x0_0_11 = 1.0
#     x0_11_9 = 1.0
#     z0 = 4.0
#     z3 = 4.0
#     z0TW9E = 7.0
#     z3TW6E = 3.0
#
# - Kết quả ra 402 for optimal cost (chỉ chạy đơn) cho 255 nodes
#     Optimal value: 402.0
#     Solution:
#     x2_2_3 = 1.0
#     x2_3_4 = 1.0
#     x2_4_5 = 1.0
#     x2_5_6 = 1.0
#     x2_6_7 = 1.0
#     x2_7_8 = 1.0
#     x2_8_9 = 1.0
#     x2_9_16 = 1.0
#     x24_24_25 = 1.0
#     x24_46_36 = 1.0
#     x24_36_37 = 1.0
#     x24_37_38 = 1.0
#     x24_38_39 = 1.0
#     x24_39_40 = 1.0
#     x24_45_46 = 1.0
#     x24_25_45 = 1.0
#     x2_16_254 = 1.0
#     x24_40_255 = 1.0
# """
# for source in exclude_i:
#     for node in zero_demand_supply:
#         arcs_dict_in = zero_demand_supply_node_dict_in.get(node, [])
#         arcs_dict_out = zero_demand_supply_node_dict_out.get(node, [])
#         sum_arc_in = quicksum(var_dict[f"x{source}_{i}_{j}"] for i, j in arcs_dict_in)
#         sum_arc_out = quicksum(var_dict[f"x{source}_{i}_{j}"] for i, j in arcs_dict_out)
#         print(f"Sum arc in: {sum_arc_in}")
#         print(f"Sum arc out: {sum_arc_out}")
#         model.addCons(sum_arc_in == sum_arc_out)


# """
# Phương pháp tính toán ràng buộc ràng buộc khác:
# - Với mỗi điểm không có demand, tổng đầu vào bằng tổng đầu ra cho cả 2 xe
#     x0_3_2 + x3_3_2 == x0_2_0 + x3_2_0
#     x0_6_5 + x3_6_5 == x0_5_3 + x3_5_3
# - Kết quả cho supply_03_demand_69.txt:
#     Optimal value: 18.0
#     Solution:
#     x3_3_6 = 1.0
#     x0_0_11 = 1.0
#     x0_11_9 = 1.0
#     z0 = 4.0
#     z3 = 4.0
#     z0TW9E = 7.0
#     z3TW6E = 3.0
#
# - Kết quả ra 402 for optimal cost (chỉ chạy đơn) cho 255 nodes
#     Optimal value: 402.0
#     Solution:
#     x2_2_3 = 1.0
#     x2_3_4 = 1.0
#     x2_4_5 = 1.0
#     x2_5_6 = 1.0
#     x2_6_7 = 1.0
#     x2_7_8 = 1.0
#     x2_8_9 = 1.0
#     x2_9_16 = 1.0
#     x24_24_25 = 1.0
#     x24_46_36 = 1.0
#     x24_36_37 = 1.0
#     x24_37_38 = 1.0
#     x24_38_39 = 1.0
#     x24_39_40 = 1.0
#     x24_45_46 = 1.0
#     x24_25_45 = 1.0
#     x2_16_254 = 1.0
#     x24_40_255 = 1.0
# """
# for node in zero_demand_supply:
#     arcs_dict_in = zero_demand_supply_node_dict_in.get(node, [])
#     arcs_dict_out = zero_demand_supply_node_dict_out.get(node, [])
#     for source in exclude_i:
#         sum_arc_in = quicksum(var_dict[f"x{source}_{i}_{j}"] for i, j in arcs_dict_in)
#         sum_arc_out = quicksum(var_dict[f"x{source}_{i}_{j}"] for i, j in arcs_dict_out)
#         model.addCons(sum_arc_in == sum_arc_out)



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
    #src_outbound_arc[source] = [var for var in all_vars if f"_{source}_" in var.name]
    #src_inbound_arc[source] = [var for var in all_vars if var.name[-1] == source]
    # init inbound arc
    src_inbound_arc.setdefault(source, [])
    # init outbound arc
    src_outbound_arc.setdefault(source, [])
    for var in all_vars:
        # split var name with delimiter '_'
        parts = var.name.split('_')

        # check if last part is source
        if parts[-1] == source:
            src_inbound_arc[source].append(var)
        if parts[1] == source:
            src_outbound_arc[source].append(var)
print(f"src_outbound_arc: {src_outbound_arc}")
print(f"src_inbound_arc: {src_inbound_arc}")

"""
output of outbound_arc and inbound_arc
outbound: {'3': [x3_3_6, x0_3_6, x3_3_2, x0_3_2], '0': [x3_0_3, x0_0_3, x3_0_11, x0_0_11]}
inbound: {'3': [x3_0_3, x0_0_3, x3_5_3, x0_5_3], '0': [x3_9_0, x0_9_0, x3_2_0, x0_2_0]}
"""
# Huy: dựa vào outbound và inbound để thêm ràng buộc
for source in exclude_i:
    out_sum = quicksum(src_outbound_arc[source])
    #print(f"out_sum: {out_sum}")
    in_sum = 1 + quicksum(src_inbound_arc[source])
    #print(f"in_sum: {in_sum}")
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
    #dest_outbound_arc[dest] = [var for var in all_vars if f"_{dest}_" in var.name]
    #dest_inbound_arc[dest] = [var for var in all_vars if var.name[-1] == dest]
    # init inbound arc
    dest_inbound_arc.setdefault(dest, [])
    # init outbound arc
    dest_outbound_arc.setdefault(dest, [])
    for var in all_vars:
        # split var name with delimiter '_'
        parts = var.name.split('_')

        # check if last part is dest
        if parts[-1] == dest:
            dest_inbound_arc[dest].append(var)
        if parts[1] == dest:
            dest_outbound_arc[dest].append(var)
print(f"dest_outbound_arc: {dest_outbound_arc}")
print(f"dest_inbound_arc: {dest_inbound_arc}")

for dest in exclude_j:
    out_sum = 1 + quicksum(dest_outbound_arc[dest])
    #print(f"out_sum: {out_sum}")
    in_sum = quicksum(dest_inbound_arc[dest])
    #print(f"in_sum: {in_sum}")
    model.addCons(out_sum == in_sum)




"""
cách tính toán ràng buộc:
- tính chi phí tối ưu
- tạo biến z{source} để lưu trữ chi phí tối ưu
"""
# Huy: Tạo z{source}(z0, z3) để lưu trữ chi phí tối ưu

if len(earliness_and_tardiness) > 0:
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
            # split var name with delimiter '_'
            parts = var.name.split('_')
            if (f"x{source}" in var.name) and (parts[-1] == dest):
                z_vars_src_dest[var.name] = var
        # tìm gía trị của tardiness và earliness
        earliness, tardiness = earliness_and_tardiness[dest]

        # thêm ràng buộc để tính earliness và tardiness
        vars_sum = quicksum(z_vars_src_dest.values())

        model.addCons(z_var_tw_t >= (z_var - tardiness) * vars_sum)
        model.addCons(z_var_tw_e >= (earliness * vars_sum) - z_var)
        model.addCons(z_var_tw_e >= 0)
        model.addCons(z_var_tw_t >= 0)




# Huy: Tính chi phí tối ưu
if len(earliness_and_tardiness) > 0:
    alpha = 1
    beta = 1
    # Huy: Tính chi phí tối ưu
    # alpha with z_vars
    alpha_sum = quicksum(alpha * z_var for z_var in z_vars.values())
    # beta with z_vars_tw
    beta_sum = quicksum(beta * z_var_tw for (_, _), (z_var_tw_e, z_var_tw_t) in z_vars_tw.items() for z_var_tw in (z_var_tw_e, z_var_tw_t))
    model.setObjective(alpha_sum + beta_sum, "minimize")
else:
    print("Không có biến z")
    model.setObjective(quicksum(vars_and_costs[var.name] * var_dict[var.name] for var in all_vars if var.name in var_dict), "minimize")
    #model.setObjective(quicksum(vars_and_costs[var_name] * var_dict[var_name] for var_name in vars_and_costs), "minimize")

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

