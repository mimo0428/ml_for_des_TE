import numpy as np 
import pandas as pd
from pandas import DataFrame
import os

import sys
sys.path.append('..')

from network import get_network, get_weak_connected_network, get_strong_connected_network, load_network, topology_reduction
from optimization import initialize_destination_based, initialize_original, initialize_combine, solve_destination_based, solve_original, correction, solve_greedy, solve_proportional, solve_combine_4, solve_combine_5
from show import draw_hist, draw_log_hist, draw_heatmap
from optimization_gurobi import solve_destination_based_gurobi, solve_original_gurobi
from modifyNetwork import modifyA, modifyD
from readData import readname,setRamdom

from sys import maxsize
import time


# 只求解des-based
# 设置边带宽无穷，获得边上带宽占用量


if __name__=="__main__":
    # # The network that we want to load 
    # # If network_name = 0, generate a network with n nodes and p of fully connected edges.
    # network_list = readname()
    # network_list = ['Arpanet196912','Airtel', 'Gambia','Itnet' , 'Cudi' ]
    # network_list = ['Cudi']
    # network_list = [
    #         'Telcove' ,'Ion']
            #  'Colt' ,'Avg' , 'Kdl']
            
    # network_name = 'Itnet'
    n = 20
    p = 0.3
    alpha = 0
    capacity = maxsize
    

    network_list, Demand_list, filename_list = readname()
    # print("!!!!!!!!!!!!!!!!!!")
    # print(network_list,Demand_list)
    # network_list, Demand_list, filename_list = setRamdom()

    file_path2 = './result_link/link_demand.xlsx'
    
    np.random.seed(0)
    
    for i_topo in range(len(network_list)):
        

        network_name = network_list[i_topo]
        Demand = Demand_list[i_topo]
        file_name = filename_list[i_topo]
        
        print("############################")
        print(network_name)
        print("############################")
        
        csvPath = './result_link/' + network_name + '/' + file_name + '.csv'
        
        topology, A = load_network(network_name)

        link_list = []
        link_list.append(network_name) 
        
        n = np.shape(A)[0]
        m = np.shape(A)[1]
        link_list.append(n) 
        link_list.append(m) 
         


        # topology_size
        # 0: original 1: reduced
        # algorithm 
        # 0: original method  1: destination-based method  
        # solver
        # 0: cvxpy  1: gurobi
        
        F_variable, c, zero, one = initialize_destination_based(A)  
        c = capacity
        F, time_1, optimal, status = solve_destination_based_gurobi(alpha, A, c, zero, one, Demand)
        F = correction(F)
        Z1, time_2 = solve_greedy(A, F.copy())
        
        colF = sorted(F.sum(axis=0))
        
        link_list.append(colF[0])
        link_list.append(colF[int(m/2)])
        link_list.append(colF[int(m*4/5)])
        link_list.append(colF[m-1])
        
        # 放入csv
        data = pd.DataFrame(F)
        data.to_csv(csvPath) 


        data_link = pd.read_excel(file_path2, header = [0])
        
        link_list.append(file_name)
        data_link.loc[len(data_link)] = link_list
        
        excelWriter = pd.ExcelWriter(file_path2, engine='openpyxl') 
        DataFrame(data_link).to_excel(excel_writer=excelWriter, index=False, header=True)

        excelWriter.save()
        excelWriter.close()        

    # print(np.average(time_list,axis = 0))
    # print(np.sum(np.average(time_list,axis = 0)))
    # print(np.average(optimal_list))
