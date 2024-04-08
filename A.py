from pyscipopt import Model, quicksum

model = Model("Simple linear max optimization")

x0_0_3 = model.addVar(vtype="B", name=f"x0_0_3")
x0_3_6 = model.addVar(vtype="B", name=f"x0_3_6")
x0_6_9 = model.addVar(vtype="B", name=f"x0_6_9")
x0_9_0 = model.addVar(vtype="B", name=f"x0_9_0")

x0_0_11 = model.addVar(vtype="B", name=f"x0_0_11")
x0_11_9 = model.addVar(vtype="B", name=f"x0_11_9")
x0_9_8 = model.addVar(vtype="B", name=f"x0_9_8")
x0_8_6 = model.addVar(vtype="B", name=f"x0_8_6")

x0_6_5 = model.addVar(vtype="B", name=f"x0_6_5")
x0_5_3 = model.addVar(vtype="B", name=f"x0_5_3")
x0_3_2 = model.addVar(vtype="B", name=f"x0_3_2")
x0_2_0 = model.addVar(vtype="B", name=f"x0_2_0")

x3_0_3 = model.addVar(vtype="B", name=f"x3_0_3")
x3_3_6 = model.addVar(vtype="B", name=f"x3_3_6")
x3_6_9 = model.addVar(vtype="B", name=f"x3_6_9")
x3_9_0 = model.addVar(vtype="B", name=f"x3_9_0")

x3_0_11 = model.addVar(vtype="B", name=f"x3_0_11")
x3_11_9 = model.addVar(vtype="B", name=f"x3_11_9")
x3_9_8 = model.addVar(vtype="B", name=f"x3_9_8")
x3_8_6 = model.addVar(vtype="B", name=f"x3_8_6")

x3_6_5 = model.addVar(vtype="B", name=f"x3_6_5")
x3_5_3 = model.addVar(vtype="B", name=f"x3_5_3")
x3_3_2 = model.addVar(vtype="B", name=f"x3_3_2")
x3_2_0 = model.addVar(vtype="B", name=f"x3_2_0")

#Ràng buộc về điểm xuất phát của xe 0 và xe 3
model.addCons(x0_0_11 + x0_0_3 == 1) #xe 0 sẽ rời 0 theo hướng đến 11 hoặc đến 3
model.addCons(x3_3_2 + x3_3_6 == 1) #xe 3 sẽ rời 3 theo hướng đến 2 hoặc đến 6

# Ràng buộc về điểm đích của xe 0 và xe 3
model.addCons(x0_11_9 + x0_6_9 + x3_11_9 + x3_6_9 == 1) #xe 0 hoặc xe 3 sẽ đến đây
model.addCons(x0_3_6 + x0_8_6 + x3_3_6 + x3_8_6 == 1) #xe 0 hoặc xe 3 sẽ đến đây

#Ràng buộc về capacity trên các cung mà xe 0 hoặc xe 3 đi qua
model.addCons(x0_0_3 + x3_0_3 <= 1)
model.addCons(x0_3_6 + x3_3_6 <= 1)
model.addCons(x0_6_9 + x3_6_9 <= 1)
model.addCons(x0_9_0 + x3_9_0 <= 1)
model.addCons(x0_0_11 + x3_0_11 <= 1)
model.addCons(x0_11_9 + x3_11_9 <= 1) #xe 0 hoặc xe 3 qua cung này đây
model.addCons(x0_9_8 + x3_9_8 <= 1)
model.addCons(x0_8_6 + x3_8_6 <= 1)
model.addCons(x0_6_5 + x3_6_5 <= 1)
model.addCons(x0_5_3 + x3_5_3 <= 1)
model.addCons(x0_3_2 + x3_3_2 <= 1) #xe 0 hoặc xe 3 sẽ đến đây
model.addCons(x0_2_0 + x3_2_0 <= 1)

#Ràng buộc về liên thông
#trừ các điểm nguồn/đích, tổng luồng đi vào của 1 điểm
#bằng tổng luồng đi ra của 1 điểm
model.addCons(x0_3_2 == x0_2_0)
model.addCons(x3_3_2 == x3_2_0)

model.addCons(x0_6_5 == x0_5_3)
model.addCons(x3_6_5 == x3_5_3)

model.addCons(x0_9_8 == x0_8_6)
model.addCons(x3_9_8 == x3_8_6)

model.addCons(x0_0_11 == x0_11_9)
model.addCons(x3_0_11 == x3_11_9)

#ràng buộc về liên thông cho điểm nguồn
model.addCons(x0_0_11 + x0_0_3 == 1 + x0_2_0 + x0_9_0)
model.addCons(x3_0_11 + x3_0_3 == x3_2_0 + x3_9_0)
#model.addCons(x0_0_11 + x3_0_11 + x0_0_3 + x3_0_3 == 1 + x0_2_0 + x3_2_0 + x0_9_0 + x3_9_0)
#model.addCons(x0_3_2 + x3_3_2 + x0_3_6 + x3_3_6 == 1 + x0_0_3 + x3_0_3 + x0_5_3 + x3_5_3)
model.addCons(x0_3_2 + x0_3_6 == x0_0_3 + x0_5_3)
model.addCons(x3_3_2 + x3_3_6 == 1 + x3_0_3 + x3_5_3)

#ràng buộc về liên thông cho điểm đích
#model.addCons(x0_11_9 + x0_6_9 + x3_11_9 + x3_6_9 == 1)
model.addCons(x0_11_9 + x3_11_9 + x0_6_9 + x3_6_9 == 1 + x0_9_8 + x3_9_8 + x0_9_0 + x3_9_0)
model.addCons(x0_6_9 + x3_6_9 + x0_6_5 + x3_6_5 + 1 == x0_3_6 + x3_3_6 + x0_8_6 + x3_8_6)

#khai báo biến mới
z0 = model.addVar(vtype = "I", name=f"z0")
model.addCons(z0 == 4*x0_0_3 + 4*x0_3_6 + 4*x0_6_9 + 4*x0_9_0 + 2*x0_0_11 + 2*x0_11_9 + 2*x0_9_8 + 2*x0_8_6 + 2*x0_6_5 + 2*x0_5_3 + 2*x0_3_2 + 2*x0_2_0)

z0TW6E = model.addVar(vtype = "C", name=f"z0TW6E")
z0TW6T = model.addVar(vtype = "C", name=f"z0TW6T")
#model.addCons(z0TW1T >= z0 - 9*x0_3_6 - 9*x0_8_6)
model.addCons(z0TW6T >= (z0 - 9)*(x0_3_6 + x0_8_6))
model.addCons(z0TW6E >= 7*x0_3_6 + 7*x0_8_6 - z0)
model.addCons(z0TW6E >= 0)
model.addCons(z0TW6T >= 0)

z0TW9E = model.addVar(vtype = "C", name=f"z0TW9E")
z0TW9T = model.addVar(vtype = "C", name=f"z0TW9T")
#model.addCons(z0TW2T >= z0 - 13*x0_6_9 - 13*x0_11_9)
model.addCons(z0TW9T >= (z0 - 13)*(x0_6_9 + x0_11_9))
model.addCons(z0TW9E >= 11*x0_6_9 + 11*x0_11_9 - z0)
model.addCons(z0TW9E >= 0)
model.addCons(z0TW9T >= 0)


z3 = model.addVar(vtype = "I", name=f"z3")
model.addCons(z3 == 4*x3_0_3 + 4*x3_3_6 + 4*x3_6_9 + 4*x3_9_0 + 2*x3_0_11 + 2*x3_11_9 + 2*x3_9_8 + 2*x3_8_6 + 2*x3_6_5 + 2*x3_5_3 + 2*x3_3_2 + 2*x3_2_0)
z3TW6E = model.addVar(vtype = "C", name=f"z3TW6E")
z3TW6T = model.addVar(vtype = "C", name=f"z3TW6T")
#model.addCons(z3TW1T >= z3 - 9*x3_3_6 - 9*x3_8_6)
model.addCons(z3TW6T >= (z3 - 9)*(x3_3_6 + x3_8_6))
model.addCons(z3TW6E >= 7*x3_3_6 + 7*x3_8_6 - z3)
model.addCons(z3TW6E >= 0)
model.addCons(z3TW6T >= 0)

z3TW9E = model.addVar(vtype = "C", name=f"z3TW9E")
z3TW9T = model.addVar(vtype = "C", name=f"z3TW9T")
#model.addCons(z3TW2T >= z3 - 13*x3_6_9 - 13*x3_11_9)
model.addCons(z3TW9T >= (z3 - 13)*(x3_6_9 + x3_11_9))
model.addCons(z3TW9E >= 11*x3_6_9 + 11*x3_11_9 - z3)
model.addCons(z3TW9E >= 0)
model.addCons(z3TW9T >= 0)

alpha = 1
beta = 1
model.setObjective(alpha*z0 + alpha*z3 + beta*z0TW6T + beta*z0TW6E + beta*z0TW9T + beta*z0TW9E + beta*z3TW6T + beta*z3TW6E + beta*z3TW9T + beta*z3TW9E, "minimize")
#model.setObjective(4*x0_0_3 + 4*x3_0_3 + 4*x0_3_6 + 4*x3_3_6 + 4*x0_6_9 + 4*x3_6_9 + 4*x0_9_0 + 4*x3_9_0 + 2*x0_0_11 + 2*x3_0_11 + 2*x0_11_9 + 2*x3_11_9 + 2*x0_9_8 + 2*x3_9_8 + 2*x0_8_6 + 2*x3_8_6 + 2*x0_6_5 + 2*x3_6_5 + 2*x0_5_3 + 2*x3_5_3 + 2*x0_3_2 + 2*x3_3_2 + 2*x0_2_0 + 2*x3_2_0, "minimize")
#model.setObjective(z0TW1E + z0TW1T + z0TW2E + z0TW2T + z3TW1E + z3TW1T + z3TW2E + z3TW2T, "minimize")

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

