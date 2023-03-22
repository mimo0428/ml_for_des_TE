import gurobipy as grb
import numpy as np

if __name__ == "__main__":
    m = grb.Model("LP")
    m.setParam('OutputFlag', 1)
    
    
    # y = m.addMVar((3,2), lb=0, ub=grb.GRB.INFINITY) # 1x2

    # m.addGenConstrPow(x, y ,2,name = 'tempow')
    
    c = np.array([1,2,3]) #1x2

    x = m.addMVar((3,2), lb=0, ub=grb.GRB.INFINITY) # 3x2
    A1 = np.full(3, 1) #3x1
    b = np.full(2, 1) #2x1
    
    m.addMConstr(x.T, A1, '<=', b)


    # m.addConstr(x.T @ A1 <= b)

    print(x.shape)
    
    m.Params.timelimit = 9999999999999999999999
    
    m.setObjective(x[:,0] @ c, grb.GRB.MAXIMIZE)
    
    m.update()
    m.optimize()
    # print(x.X)
    # print('x_1={}'.format(x[0][0].X))
    # print('x_2={}'.format(x[1][0].X))
    

    m.write('test.lp')