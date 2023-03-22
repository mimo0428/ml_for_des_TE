import gurobipy as grb
import numpy as np
import time

def solve_original_gurobi(alpha, A, c, zero, zero_2, one, mask,Demand):

    n = np.shape(A)[0]
    m = np.shape(A)[1]
    print(n,m)

    model = grb.Model("des")
    model.setParam('OutputFlag', 1)
    pow_T = {}

    print('!!Start set consrtaint!!')
    step1_start = time.time()
    Z = model.addMVar((n*n, m), vtype=grb.GRB.CONTINUOUS , lb=0, ub=grb.GRB.INFINITY, name = 'Z')
    
    tem_Z = {}

    F = model.addMVar((n, m), vtype=grb.GRB.CONTINUOUS , lb=0, ub=grb.GRB.INFINITY, name = 'F')
    T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=-grb.GRB.INFINITY,ub=grb.GRB.INFINITY , name = 'T')
    tem_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0,ub=grb.GRB.INFINITY , name = 'tem_T')
    # pow_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0, ub=grb.GRB.INFINITY)

    for j in range(n):
        for k in range(m):
            obj = grb.LinExpr(0)
            tem_Z[j,k] = {}
            for i in range(n):
                tem_Z[j,k][i] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0,
                    ub=grb.GRB.INFINITY)
                model.addConstr(tem_Z[j,k][i] == Z[i+j*n][k], name = 'temZ')
                obj.addTerms(1, tem_Z[j,k][i])

            model.addConstr(F[j][k] == obj , name = 'FZ')


    # model.addConstr(F >= zero, name = 'zero')
    model.addConstr(F.T @ one <= c , name = 'capacity')
    model.addConstr(T + F @ A.T == 0 , name = 'TF')
    model.addConstr(mask * (Z @ A.T) == zero_2, name = 'mask')
    
    # 设置目标函数
    obj = grb.LinExpr(0)

    for i in range(n):
        pow_T[i] = {}
        for j in range(n):
            if i != j:
                
                pow_T[i][j] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0,
                    ub=grb.GRB.INFINITY)
                model.addConstr(T[i][j] <= Demand[i][j], name = 'demand_T')
                if alpha == 0:
                    model.addConstr(T[i][j] == pow_T[i][j], name = 'tem_T')
                else:
                    model.addConstr(T[i][j] == tem_T[i][j], name = 'tem_T')
                    model.addGenConstrPow(tem_T[i,j],pow_T[i][j],1-alpha , name = 'pow_T_' + str(i) + '_' + str(j))

                obj.addTerms(1/(1-alpha), pow_T[i][j])
    # model.addGenConstrPow(T[i,j],x1,1-alpha)
    

    model.setObjective(obj, grb.GRB.MAXIMIZE)

    

    step1_end = time.time()
    setconTime = step1_end - step1_start
    print('!!End set consrtaint!!')

    with open("time.txt","a") as f:
        f.write("original:\n")
        f.write("setconTime:\n")
        f.write(str(setconTime))
        f.write("\n")
    # print(prob.is_dcp())
    
    model.optimize()
    
    # model.computeIIS()
    # model.write("model1.ilp")

    # print("\n\n-----optimal value-----")
    # print(model.ObjVal)

    optimal_value = model.getObjective().getValue()
    
    res_T= [[0] * n] * n
    for i in range(n):
        for j in range(n):
            if i != j :
                res_T[i][j] = T[i][j].getAttr('x')

    return (Z.getAttr('x'), res_T , model.Runtime, optimal_value, 1)

def solve_destination_based_gurobi(alpha, A, c, zero, one,Demand):

    n = np.shape(A)[0]
    m = np.shape(A)[1]
    print(n,m)

    model = grb.Model("des")
    model.setParam('OutputFlag', 1)

    print('!!Start set consrtaint!!')
    step1_start = time.time()
    pow_T = {}

    F = model.addMVar((n, m), vtype=grb.GRB.CONTINUOUS , lb=0, ub=grb.GRB.INFINITY, name = 'F')
    T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=-grb.GRB.INFINITY,ub=grb.GRB.INFINITY , name = 'T')
    tem_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0,ub=grb.GRB.INFINITY , name = 'tem_T')
    # pow_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0, ub=grb.GRB.INFINITY)

    # model.addConstr(F >= zero, name = 'zero')
    model.addConstr(F.T @ one <= c , name = 'capacity')
    model.addConstr(T + F @ A.T == 0 , name = 'TF')

    # 设置目标函数
    obj = grb.LinExpr(0)

    for i in range(n):
        pow_T[i] = {}
        for j in range(n):
            if i != j:
                
                pow_T[i][j] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0,
                    ub=grb.GRB.INFINITY)
                model.addConstr(T[i][j] <= Demand[i][j], name = 'demand_T')
                if alpha == 0:
                    model.addConstr(T[i][j] == pow_T[i][j], name = 'tem_T')
                else:
                    model.addConstr(T[i][j] == tem_T[i][j], name = 'tem_T')
                    model.addGenConstrPow(tem_T[i,j],pow_T[i][j],1-alpha , name = 'pow_T_' + str(i) + '_' + str(j))
                
                # 设置目标函数    
                obj.addTerms(1/(1-alpha), pow_T[i][j])
    
    model.setObjective(obj, grb.GRB.MAXIMIZE)

    
    step1_end = time.time()
    setconTime = step1_end - step1_start
    print('!!End set consrtaint!!')

    with open("time.txt","a") as f:
        f.write("des:\n")
        f.write("setconTime:\n")
        f.write(str(setconTime))
        f.write("\n")

    # print(prob.is_dcp())
    
    model.optimize()

    # model.computeIIS()
    # model.write("model1.ilp")

    # print("\n\n-----optimal value-----")
    # print(model.ObjVal)

    optimal_value = model.getObjective().getValue()

    res_T= [[0] * n] * n
    for i in range(n):
        for j in range(n):
            if i != j :
                res_T[i][j] = T[i][j].getAttr('x')

    return (F.getAttr('x') ,res_T , model.Runtime, optimal_value, 1)

def solve_destination_based_gurobi_2(alpha, A, c, zero, one,Demand):

    n = np.shape(A)[0]
    m = np.shape(A)[1]
    print(n,m)

    model = grb.Model("des")
    model.setParam('OutputFlag', 1)

    print('!!Start set consrtaint!!')
    step1_start = time.time()
    T = {}
    
    # F = model.addMVar((n, m), vtype=grb.GRB.CONTINUOUS , lb=0, ub=grb.GRB.INFINITY, name = 'F')
    # T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=-grb.GRB.INFINITY,ub=grb.GRB.INFINITY , name = 'T')
    tem_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0,ub=grb.GRB.INFINITY , name = 'tem_T')
    # pow_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0, ub=grb.GRB.INFINITY)

    F = {}
    for i in range(n):
        F[i] = {}
        for e in range(m):
            F[i][e] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0, ub=grb.GRB.INFINITY , name = 'F' + str(i) + str(e))
    
    cap_con = {}
    AF = {}
    
    # 链路带宽
    for e in range(m):
        cap_con[e] = grb.LinExpr(0)
        for i in range(n):
            cap_con[e].addTerms(1, F[i][e])
        model.addConstr(cap_con[e] <= c, name = 'capacity' + str(e))
        
    # model.addConstr(F.T @ one <= c , name = 'capacity')
    # model.addConstr(T + F @ A.T == 0 , name = 'TF')

    # 设置目标函数 
    obj = grb.LinExpr(0)

    for i in range(n):
        T[i] = {}
        AF[i] = {}
        for j in range(n):
            if i != j:
                
                T[i][j] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0,
                    ub=grb.GRB.INFINITY)
                
                
                model.addConstr(T[i][j] <= Demand[i][j], name = 'demand_T' + str(i) + str(j))
                # 设置目标函数    
                obj.addTerms(1/(1-alpha), T[i][j])
                
                AF[i][j] = grb.LinExpr(0)
                # 设置F和T的转换
                for e in range(m):
                    AF[i][j].addTerms(A[j][e], F[i][e])
                    
                model.addConstr(T[i][j] + AF[i][j] == 0, name = 'T_AF' + str(i))
    
    model.setObjective(obj, grb.GRB.MAXIMIZE)

    
    step1_end = time.time()
    setconTime = step1_end - step1_start
    print('!!End set consrtaint!!')

    with open("time.txt","a") as f:
        f.write("des:\n")
        f.write("setconTime:\n")
        f.write(str(setconTime))
        f.write("\n")

    # print(prob.is_dcp())
    
    model.optimize()

    # model.computeIIS()
    # model.write("model1.ilp")

    # print("\n\n-----optimal value-----")
    # print(model.ObjVal)

    optimal_value = model.getObjective().getValue()
    
    res_F= [[0] * m] * n

    for i in range(n):
        for e in range(m):
            res_F[i][e] = F[i][e].getAttr('x')
    # print(F)
    res_T= [[0] * n] * n
    for i in range(n):
        for j in range(n):
            if i != j :
                res_T[i][j] = T[i][j].getAttr('x')
    
    return (res_F, res_T, model.Runtime, optimal_value, 1)