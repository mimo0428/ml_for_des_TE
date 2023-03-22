import numpy as np 

from network import get_network, get_weak_connected_network, get_strong_connected_network, load_network, topology_reduction, modifyA
from optimization import initialize_destination_based, initialize_original, initialize_combine, solve_destination_based, solve_original, correction, solve_greedy, solve_proportional, solve_combine_4, solve_combine_5
from show import draw_hist, draw_log_hist, draw_heatmap
from optimization_gurobi import solve_destination_based_gurobi, solve_original_gurobi


if __name__=="__main__":

    # 0: original method  1: destination-based method  2: combining columns method
    algorithm = 0

    # 0: cvxpy  1: gurobi
    solver = 1

    # The network that we want to load 
    # If network_name = 0, generate a network with n nodes and p of fully connected edges.
    network_name = 'Itnet'
    n = 20
    p = 0.3
    alpha = 0.7
    
    time_list = []
    optimal_list = []
    np.random.seed(0)

    if network_name != 0:
        # load the network with network_name
        topology, A = load_network(network_name)
        # delete nodes of a degree of 2
        reduced_A, degree_two_node_set, degree_two_node_neighbor, main_nodes = topology_reduction(topology)
        mod_A = modifyA(reduced_A)
        A = mod_A
        # print(A)
        # print('reduced_A:')
        # print(reduced_A)
        # print('mod_A:')
        # print(mod_A)
        # print("degree_two_node_set:")
        # print(degree_two_node_set)
        # print("degree_two_node_neighbor:")
        # print(degree_two_node_neighbor)
        # A = reduced_A

    for round in range(1):
        if network_name == 0:
            # Generate a network
            topology, A, connected = get_strong_connected_network(n, p)

        n = np.shape(A)[0]
        m = np.shape(A)[1]

        if network_name != 0 or connected:
            if algorithm == 0:
                # 0: original method
                Z_variable, c, zero, zero_2, one, mask = initialize_original(A)
                if solver == 0:
                    Z, time, optimal, status = solve_original(alpha, A, Z_variable, c, zero, zero_2, one, mask)
                if solver == 1:
                    Z, time, optimal, status = solve_original_gurobi(alpha, A, c, zero, zero_2, one, mask)

                time_list.append(time)
                optimal_list.append(optimal)

            elif algorithm == 1:
                # 1: destination-based method
                F_variable, c, zero, one = initialize_destination_based(A)  
                if solver == 0:
                    F, time_1, optimal, status = solve_destination_based(alpha, A, F_variable, c, zero, one)
                elif solver == 1:
                    F, time_1, optimal, status = solve_destination_based_gurobi(alpha, A, c, zero, one)

                F = correction(F)
                # print(F)
                Z1, time_2 = solve_greedy(A, F.copy())
                # Z2, time_2 = solve_proportional(A, F.copy())
                
                # draw_heatmap(-F @ A.T)
                # draw_hist(-F @ A.T)
                # draw_log_hist(-F @ A.T)

                time_list.append([time_1, time_2])
                optimal_list.append(optimal)

            elif algorithm == 2:
                # 2: combining columns method
                if np.shape(A)[1] % 2 == 0:
                    F_combine_variable, F_half_variable, c, zero, one = initialize_combine(A)
                    F_combine, time_1, optimal, status = solve_combine_4(0.95, A, F_combine_variable, c, zero, one)
                    F_half, time_2, optimal, status = solve_combine_5(0.95, A, F_half_variable, F_combine, c, zero, one)
                    
                    F = np.zeros((n,m))
                    F[:, 0:m:2] = F_half
                    F[:, 1:m:2] = F_combine - F_half
                    F = correction(F)

                    # Z1, time_3 = solve_greedy(A, F.copy())
                    T = - F @ A.T

                    optimal = np.sum(np.power(np.abs(np.triu(T, 1)), 1-0.7)+ np.power(np.abs(np.triu(T.T, 1)), 1-0.7)) / (1-0.7)
                    time_list.append([time_1, time_2])
                    optimal_list.append(optimal)

                else:
                    print('Number of edges is odd!')

    print(np.average(time_list,axis = 0))
    print(np.sum(np.average(time_list,axis = 0)))
    print(np.average(optimal_list))
