import numpy as np
def modifyA(A):
    mod_A = A[[not np.all(A[i] == 0) for i in range(A.shape[0])], :]
    return mod_A

def modifyD(reduced_A,Demand):
    # print(reduced_A.shape)
    # print(Demand.shape)
    del_list = np.where(~reduced_A.any(axis=1))[0]
    # print(Demand)
    mod_Demand = np.delete(Demand, del_list , axis = 0)
    mod_Demand = np.delete(mod_Demand, del_list , axis = 1)

    return mod_Demand