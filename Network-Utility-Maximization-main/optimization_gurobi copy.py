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
    
    for i in range(n):
        pow_T[i] = {}
        for j in range(n):
            if i != j:
                
                pow_T[i][j] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0,
                    ub=grb.GRB.INFINITY)
                model.addConstr(T[i][j] == Demand[i][j], name = 'demand_T')
                if alpha == 0:
                    model.addConstr(T[i][j] == pow_T[i][j], name = 'tem_T')
                else:
                    model.addConstr(T[i][j] == tem_T[i][j], name = 'tem_T')
                    model.addGenConstrPow(tem_T[i,j],pow_T[i][j],1-alpha , name = 'pow_T_' + str(i) + '_' + str(j))
    
    # model.addGenConstrPow(T[i,j],x1,1-alpha)
    # 设置目标函数
    obj = grb.LinExpr(0)
    for i in range(n):
        for j in range(n):
            if i != j:
                obj.addTerms(1/(1-alpha), pow_T[i][j])

    model.setObjective(obj, grb.GRB.MAXIMIZE)

    
    
    # print(prob.is_dcp())
    step1_start = time.time()
    model.optimize()
    step1_end = time.time()
    # model.computeIIS()
    # model.write("model1.ilp")

    # print("\n\n-----optimal value-----")
    # print(model.ObjVal)

    optimal_value = model.getObjective().getValue()

    return (Z.getAttr('x'), model.Runtime, optimal_value, 1)

def solve_destination_based_gurobi(alpha, A, c, zero, one,Demand):

    n = np.shape(A)[0]
    m = np.shape(A)[1]
    print(n,m)

    model = grb.Model("des")
    model.setParam('OutputFlag', 1)
    pow_T = {}

    F = model.addMVar((n, m), vtype=grb.GRB.CONTINUOUS , lb=0, ub=grb.GRB.INFINITY, name = 'F')
    T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=-grb.GRB.INFINITY,ub=grb.GRB.INFINITY , name = 'T')
    tem_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0,ub=grb.GRB.INFINITY , name = 'tem_T')
    # pow_T = model.addMVar((n, n), vtype=grb.GRB.CONTINUOUS, lb=0, ub=grb.GRB.INFINITY)

    # model.addConstr(F >= zero, name = 'zero')
    model.addConstr(F.T @ one <= c , name = 'capacity')
    model.addConstr(T + F @ A.T == 0 , name = 'TF')
    for i in range(n):
        pow_T[i] = {}
        for j in range(n):
            if i != j:
                
                pow_T[i][j] = model.addVar(vtype=grb.GRB.CONTINUOUS,lb=0,
                    ub=grb.GRB.INFINITY)
                model.addConstr(T[i][j] == Demand[i][j], name = 'demand_T')
                if alpha == 0:
                    model.addConstr(T[i][j] == pow_T[i][j], name = 'tem_T')
                else:
                    model.addConstr(T[i][j] == tem_T[i][j], name = 'tem_T')
                    model.addGenConstrPow(tem_T[i,j],pow_T[i][j],1-alpha , name = 'pow_T_' + str(i) + '_' + str(j))

    # 设置目标函数
    obj = grb.LinExpr(0)
    for i in range(n):
        for j in range(n):
            if i != j:
                obj.addTerms(1/(1-alpha), pow_T[i][j])
                # obj.addTerms(1, pow_T[i][j])

    model.setObjective(obj, grb.GRB.MAXIMIZE)

    
    
    # print(prob.is_dcp())
    step1_start = time.time()
    model.optimize()
    step1_end = time.time()
    # model.computeIIS()
    # model.write("model1.ilp")

    # print("\n\n-----optimal value-----")
    # print(model.ObjVal)

    optimal_value = model.getObjective().getValue()

    return (F.getAttr('x'), model.Runtime, optimal_value, 1)
