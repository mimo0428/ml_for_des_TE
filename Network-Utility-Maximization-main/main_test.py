import numpy as np 
import pandas as pd
from pandas import DataFrame
import os

from network import get_network, get_weak_connected_network, get_strong_connected_network, load_network, topology_reduction
from optimization import initialize_destination_based, initialize_original, initialize_combine, solve_destination_based, solve_original, correction, solve_greedy, solve_proportional, solve_combine_4, solve_combine_5
from show import draw_hist, draw_log_hist, draw_heatmap
from optimization_gurobi import solve_destination_based_gurobi, solve_original_gurobi
from modifyNetwork import modifyA

def readname():
    topoPath = '../archive'
    filename = os.listdir(topoPath)
    name = []
    for i in filename:
        portion = os.path.splitext(i)   #把文件名拆分为名字和后缀
        if portion[1] == ".gml":
            name.append(portion[0])
    print(len(name))
    return name


if __name__=="__main__":
    # # The network that we want to load 
    # # If network_name = 0, generate a network with n nodes and p of fully connected edges.
    # network_list = readname()
    # network_list = ['Arpanet196912','Airtel', 'Gambia','Itnet' , 'Cudi' ]
    # network_list = ['Cudi']
    network_list = [
            'Telcove' ,'Ion']
            #  'Colt' ,'Avg' , 'Kdl']
            
    # network_name = 'Itnet'
    n = 20
    p = 0.3
    alpha = 0


    file_path = './res_solver_ori.xlsx'
    file_path2 = './res_solver_' + str(alpha) + '_part.xlsx'
    data_time = pd.read_excel(file_path2, sheet_name = 'time',header = [0])
    data_value = pd.read_excel(file_path2, sheet_name = 'optimal_value',header = [0])
    print(data_time.columns)
    print(data_time.index)
    
    
    print(data_time)

    # # 0: original method  1: destination-based method  2: combining columns method
    # algorithm = 0

    # # 0: cvxpy  1: gurobi
    # solver = 1

    
    
    
    np.random.seed(0)
    
    for i_topo in range(len(network_list)):
        network_name = network_list[i_topo]
        
        print("############################")
        print(network_name)
        print("############################")
        
        
        topology, A = load_network(network_name)
        # delete nodes of a degree of 2
        reduced_A, degree_two_node_set, degree_two_node_neighbor, main_nodes = topology_reduction(topology)
        mod_A = modifyA(reduced_A)

        time_list = []
        time_list.append(network_name) 
        n = np.shape(A)[0]
        m = np.shape(A)[1]
        time_list.append(n) 
        time_list.append(m) 

        n_r = np.shape(mod_A)[0]
        m_r = np.shape(mod_A)[1]
        time_list.append(n_r) 
        time_list.append(m_r)

        optimal_list = []
        optimal_list.append(network_name)

        # topology_size
        # 0: original 1: reduced
        # algorithm 
        # 0: original method  1: destination-based method  
        # solver
        # 0: cvxpy  1: gurobi

        for is_reduced in range(2):
            if is_reduced == 1:
                A = mod_A
            n = np.shape(A)[0]
            m = np.shape(A)[1]

            for algorithm in range(2):
                if algorithm == 0:
                    # 0: original method
                    Z_variable, c, zero, zero_2, one, mask = initialize_original(A)
                    for solver in range(2):
                        if solver == 0:
                            Z, time, optimal, status = solve_original(alpha, A, Z_variable, c, zero, zero_2, one, mask)
                        elif solver == 1:
                            Z, time, optimal, status = solve_original_gurobi(alpha, A, c, zero, zero_2, one, mask)
                        time_list.append(time)
                        optimal_list.append(optimal)
                    

                elif algorithm == 1:
                    # 1: destination-based method
                    F_variable, c, zero, one = initialize_destination_based(A)      
                    for solver in range(2):
                        if solver == 0:
                            F, time_1, optimal, status = solve_destination_based(alpha, A, F_variable, c, zero, one)
                        elif solver == 1:
                            F, time_1, optimal, status = solve_destination_based_gurobi(alpha, A, c, zero, one)

                        F = correction(F)
                        Z1, time_2 = solve_greedy(A, F.copy())
                        # Z2, time_2 = solve_proportional(A, F.copy())
                        
                        # draw_heatmap(-F @ A.T)
                        # draw_hist(-F @ A.T)
                        # draw_log_hist(-F @ A.T)

                        time_list.append(time_1+time_2)
                        optimal_list.append(optimal)

        print(len(time_list))
        data_time.loc[len(data_time)] = time_list
        data_value.loc[len(data_value)] = optimal_list


    excelWriter = pd.ExcelWriter(file_path2, engine='openpyxl') 
    DataFrame(data_time).to_excel(excel_writer=excelWriter, sheet_name='time', index=False, header=True)
    DataFrame(data_value).to_excel(excel_writer=excelWriter, sheet_name='optimal_value', index=False, header=True)
    
    excelWriter.save()
    excelWriter.close()        
    # print(np.average(time_list,axis = 0))
    # print(np.sum(np.average(time_list,axis = 0)))
    # print(np.average(optimal_list))
