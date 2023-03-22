import numpy as np 

def load_network(network_name):
    n = 0
    m = 0
    i = 0
    j = 0

    with open('archive/' + network_name + '.gml', "r") as f:
        line_list = f.readlines()
        num_line = len(line_list)
        k = 0
        while k < num_line:
            if 'node [' in line_list[k]:
                n = n + 1
            if 'edge [' in line_list[k]:
                break
            k = k + 1
        topology = np.zeros((n, n))
        while k < num_line:
            if 'source ' in line_list[k]:
                line = line_list[k].strip()
                i = int(line[7:])
                k = k + 1
                line = line_list[k].strip()
                j = int(line[7:])
                topology[i, j] = 1
                topology[j, i] = 1
                m = m + 2
            k = k + 1

    edge_list = []
    
    for j in range(n):
        for i in range(n):
            if topology[i,j] == 1:
                edge = [0] * n
                edge[i] = -1
                edge[j] = 1
                edge_list.append(edge)
    A = np.array(edge_list).T

    return topology, A

def topology_reduction(topology):
    print('HaHaHa')
    n = np.shape(topology)[0]
    degree_two_nodes = [i for i, row in enumerate(topology) if sum(row) == 2]
    degree_two_node_set = []
    degree_two_node_neighbor = []

    while len(degree_two_nodes) > 0:
        center_node = degree_two_nodes[0]
        connected_degree_two_nodes = [center_node]
        degree_two_nodes.remove(center_node)
        neighbors = [i for i, conn in enumerate(topology[center_node]) if conn == 1]

        global_neighbor = []

        node_left = neighbors[0]
        node_right = center_node
        while node_left in degree_two_nodes:
            degree_two_nodes.remove(node_left)
            connected_degree_two_nodes.insert(0, node_left)
            sub_neighbor = [i for i, conn in enumerate(topology[node_left]) if conn == 1]
            sub_neighbor.remove(node_right)
            node_right = node_left
            node_left = sub_neighbor[0]
        global_neighbor.append(node_left)
        
        node_left = center_node
        node_right = neighbors[1]
        while node_right in degree_two_nodes:
            degree_two_nodes.remove(node_right)
            connected_degree_two_nodes.append(node_right)
            sub_neighbor = [i for i, conn in enumerate(topology[node_right]) if conn == 1]
            sub_neighbor.remove(node_left)
            node_left = node_right
            node_right = sub_neighbor[0]
        global_neighbor.append(node_right)

        degree_two_node_set.append(connected_degree_two_nodes)
        degree_two_node_neighbor.append(global_neighbor)

    degree_two_nodes = [i for i, row in enumerate(topology) if sum(row) == 2]
    main_nodes = list(range(n))
    for node in degree_two_nodes:
        main_nodes.remove(node)
    
    edge_list = []  
    for j in main_nodes:
        for i in main_nodes:
            if topology[i,j] == 1:
                edge = [0] * n
                edge[i] = -1
                edge[j] = 1
                edge_list.append(edge)
    for neighbor in degree_two_node_neighbor:
        if neighbor[0] != neighbor[1]:
            edge = [0] * n
            edge[neighbor[0]] = -1
            edge[neighbor[1]] = 1
            edge_list.append(edge)
            edge = [0] * n
            edge[neighbor[1]] = -1
            edge[neighbor[0]] = 1
            edge_list.append(edge)

    reduced_A = np.array(edge_list).T

    return reduced_A, degree_two_node_set, degree_two_node_neighbor, main_nodes

def get_network(n, p):
    rand_connection = np.array(range(n*(n-1)))
    np.random.shuffle(rand_connection)
    rand_connection = rand_connection.reshape((n-1,n))
    rand_connection = np.where(rand_connection < p*n*(n-1), np.ones((n-1,n)), np.zeros((n-1,n)))
    topology = np.zeros((n, n))
    for i in range(n-1):
        topology[i, i+1:] = rand_connection[i, i+1:]
        topology[i+1, :i+1] = rand_connection[i, :i+1]

    edge_list = []
    
    for j in range(n):
        for i in range(n):
            if topology[i,j] == 1:
                edge = [0] * n
                edge[i] = -1
                edge[j] = 1
                edge_list.append(edge)
    A = np.array(edge_list).T

    return topology, A


def get_weak_connected_network(n, p):
    count = 0
    weak_connected = False
    while weak_connected == False and count < 1000: 
        topology, A = get_network(n, p)
        weak_connected = (len(weak_connection(topology)) == 1)
        count = count + 1
    return topology, A, weak_connected


def get_strong_connected_network(n, p):
    count = 0
    strong_connected = False
    while strong_connected == False and count < 1000: 
        topology, A = get_network(n, p)
        strong_connected = (len(weak_connection(topology)) == 1) and (len(strong_connection(topology)) == 1)
        count = count + 1
    return topology, A, strong_connected


def weak_connection(topology):
    n = np.shape(topology)[0]
    topology = np.where(topology > topology.T, topology, topology.T)
    checked_node = [0] * n
    weak_connection_list = []
    while np.min(checked_node) == 0:
        sub_list = []
        sub_list, checked_node = weak_connection_search(np.argmin(checked_node), sub_list, checked_node, topology)
        weak_connection_list.append(sub_list)
    # print(weak_connection_list)
    return weak_connection_list


def weak_connection_search(node, sub_list, checked_node, topology):
    checked_node[node] = 1
    sub_list.append(node)
    for i in np.where(topology[node] == 1)[0]:
        if checked_node[i] == 0:
            weak_connection_search(i, sub_list, checked_node, topology)
    return (sub_list, checked_node)


def strong_connection(topology):
    n = np.shape(topology)[0]
    strong_connection_list = []
    stack = []
    visit = [0] * n
    backtrack = [0] * n
    t = 0
    while np.min(visit) == 0:
        t, stack, strong_connection_list, visit, backtrack = strong_connection_search(np.argmin(visit), t, stack, strong_connection_list, visit, backtrack, topology)
    return strong_connection_list


def strong_connection_search(node, t, stack, strong_connection_list, visit, backtrack, topology):
    t = t + 1
    stack.append(node)
    visit[node] = t
    backtrack[node] = t
    for i in np.where(topology[node] == 1)[0]:
        if visit[i] == 0:
            t, stack, strong_connection_list, visit, backtrack = strong_connection_search(i, t, stack, strong_connection_list, visit, backtrack, topology)
            backtrack[node] = np.min([backtrack[node], backtrack[i]])
        elif stack.count(i) == 1:
            backtrack[node] = np.min([backtrack[node], backtrack[i]])
    if visit[node] == backtrack[node]:
        sub_list = []
        sub_list.append(stack.pop())
        while sub_list[-1] != node:
            sub_list.append(stack.pop())
        strong_connection_list.append(sub_list)
    return (t, stack, strong_connection_list, visit, backtrack)

