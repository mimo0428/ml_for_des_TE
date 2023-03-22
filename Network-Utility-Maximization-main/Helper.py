import numpy as np
import pickle

def get_satisfation(T,demand):
    n = len(T)
    sat = [[0] * n] * n
    for i in range(n):
        for j in range(n):
            if demand[i][j] != 0:
                sat[i][j] = T[i][j]/demand[i][j]
            else:
                sat[i][j] = 1
    
    return np.mean(sat)

def getRamdomTM():
    n = 125
    alpha = 1000
    scale = 64.0
    Demand=np.random.randint(0.1*alpha,0.2*alpha,size=[n,n])
    # Demand=np.random.random(size=[n,n])

    demand_path = './small_demand_add/Ion.graphml_uniform_' + str(alpha) +'_' + str(scale) +  '_0.15_traffic-matrix.pkl'
    with open(demand_path, "wb") as f:
        pickle.dump(Demand, f)
    
    print(demand_path)
    # fr = open(demand_path,'rb')
    # data = pickle.load(fr)  # 读取pkl文件的内容
    # print(data)
    # fr.close()


if __name__=="__main__":

    getRamdomTM()