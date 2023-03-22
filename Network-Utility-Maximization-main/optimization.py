import numpy as np 
import cvxpy as cp
import time


def initialize_destination_based(A):
    n = np.shape(A)[0]
    m = np.shape(A)[1]
    F = cp.Variable((n, m))
    zero = np.zeros((n, m))
    one = np.ones((n, 1))
    c = np.round(np.random.rand(m, 1) * 80 + 300000)
    return (F, c, zero, one)


def initialize_original(A):
    n = np.shape(A)[0]
    m = np.shape(A)[1]
    Z = cp.Variable((n * n, m))
    zero = np.zeros((n * n, m))
    zero_2 = np.zeros((n * n, n))
    one = np.ones((n, 1))
    c = np.round(np.random.rand(m, 1) * 80 + 300000)
    mask = np.ones((n * n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                mask[i * n + j][i] = 0
                mask[i * n + j][j] = 0
    return (Z, c, zero, zero_2, one, mask)


def initialize_combine(A):
    n = np.shape(A)[0]
    m = np.shape(A)[1]
    F_combine = cp.Variable((n, int(m / 2)))
    F_half = cp.Variable((n, int(m / 2)))
    zero = np.zeros((n, int(m / 2)))
    one = np.ones((n, 1))
    c = np.round(np.random.rand(m, 1) * 80 + 20)
    return (F_combine, F_half, c, zero, one)


def solve_destination_based(alpha, A, F, c, zero, one):

    # alpha fairness utility
    objective = cp.Maximize(cp.sum(cp.power(cp.upper_tri(- A @ F.T), 1-alpha)+ cp.power(cp.upper_tri(- F @ A.T), 1-alpha)) / (1-alpha))
    # objective = cp.Maximize(cp.sum(cp.upper_tri(- A @ F.T)+ cp.upper_tri(- F @ A.T)))
    
    constraints =   [F >= zero,
                    F.T @ one == c]
    prob = cp.Problem(objective, constraints)

    # print(prob.is_dcp())
    step1_start = time.time()
    try:
        prob.solve()
    except Exception as e:
        return (0, 0, 0, 0)
    step1_end = time.time()

    return (F.value, step1_end - step1_start, prob.value, prob.status)


def solve_original(alpha, A, Z, c, zero, zero_2, one, mask):

    n = np.shape(A)[0]
    F = Z[0:n]
    for i in range(n-1):
        F = F + Z[(i+1) * n : (i+2) * n]
    
    objective = cp.Maximize(cp.sum(cp.power(cp.upper_tri(- A @ F.T), 1-alpha)+ cp.power(cp.upper_tri(- F @ A.T), 1-alpha)) / (1-alpha))
    # objective = cp.Maximize(cp.sum(cp.upper_tri(- A @ F.T)+ cp.upper_tri(- F @ A.T)))
    constraints =   [Z >= zero, 
                    F.T @ one == c,
                    cp.multiply(mask, Z @ A.T) == zero_2]
    prob = cp.Problem(objective, constraints)

    # print(prob.is_dcp())
    old_start = time.time()
    try:
        prob.solve()
    except Exception as e:
        return (0, 0, 0, 0)
    old_end = time.time()

    return (Z.value, old_end - old_start, prob.value, prob.status)


def solve_combine_4(alpha, A, F, c, zero, one):

    m = np.shape(A)[1]
    c_combine = c[0:m:2] + c[1:m:2]
    weight = np.diag((c[0:m:2] / (c[0:m:2] + c[1:m:2])).reshape(int(m/2)))
    A_combine =  A[:, 0:m:2] @ weight + A[:, 1:m:2] @ (np.identity(int(m/2)) - weight)

    objective = cp.Maximize(cp.sum(cp.power(cp.upper_tri(- A_combine @ F.T), 1-alpha)+ cp.power(cp.upper_tri(- F @ A_combine.T), 1-alpha)) / (1-alpha))
    constraints =   [F >= zero, 
                    F.T @ one == c_combine, 
                    cp.upper_tri(- A_combine @ F.T) >= 0, 
                    cp.upper_tri(- F @ A_combine.T) >= 0]
    prob = cp.Problem(objective, constraints)

    # print(prob.is_dcp())
    step1_start = time.time()
    prob.solve()
    step1_end = time.time()

    return (F.value, step1_end - step1_start, prob.value, prob.status)


def solve_combine_5(alpha, A, F_half, F_combine, c, zero, one):
    
    m = np.shape(A)[1]
    c_half = c[0:m:2]
    A_half = A[:, 0:m:2]
    A_half_2 = A[:, 1:m:2]

    objective = cp.Maximize(cp.sum(cp.power(cp.upper_tri(- A_half @ F_half.T - A_half_2 @ (F_combine - F_half).T), 1-alpha)+ cp.power(cp.upper_tri(- F_half @ A_half.T - (F_combine - F_half) @ A_half_2.T), 1-alpha)) / (1-alpha))
    constraints =   [F_half >= zero, 
                    F_combine - F_half >= zero,
                    F_half.T @ one == c_half, 
                    cp.upper_tri(-A_half @ F_half.T - A_half_2 @ (F_combine - F_half).T) >= 0, 
                    cp.upper_tri(-F_half @ A_half.T - (F_combine - F_half) @ A_half_2.T) >= 0]
    prob = cp.Problem(objective, constraints)

    # print(prob.is_dcp())
    step2_start = time.time()
    prob.solve()
    step2_end = time.time()

    return (F_half.value, step2_end - step2_start, prob.value, prob.status)


def correction(F):
    n = np.shape(F)[0]
    m = np.shape(F)[1]
    threshold = np.ones((n,m)) * 0.001
    error = np.where(F < threshold, F, np.zeros((n,m)))
    F = F - error
    error = np.sum(error, axis = 0)
    for j in range(m):
        F[:, j] = F[:, j] + F[:, j] * error[j] / np.sum(F[:, j])
    return F


def solve_greedy(A, F):
    
    n = np.shape(A)[0]
    m = np.shape(A)[1]
    T = - np.dot(F, A.T)
    T = T - np.diag(np.diagonal(T))
    Z = np.zeros((n, n, m))

    step2_start = time.time()
    for i in range(n):
        for j in range(n):
            if j != i:
                restdata, F, T, Z = split_greedy(T[i,j], A, F, T, Z, j, i, j)
    
    step2_end = time.time()

    return (Z, step2_end - step2_start)


def split_greedy(data, A, F, T, Z, source, destination, outgoing):

    outgoing_edges = np.where(A[outgoing] == -1)[0]

    if len(outgoing_edges) > 0:
        # print('outgoing_edges:')
        # print(F[destination, outgoing_edges])
        order = np.argsort(- F[destination, outgoing_edges])
        # print(order)
        for i in range(len(order)):
            if A[destination, outgoing_edges[order[i]]] == 1:
                if i > 0:
                    F_destination_order = order[i]
                    order[1: i + 1] = order[0: i]
                    order[0] = F_destination_order
        i = 0
        while data > 1.0e-9 and i < len(order):
            F_index = outgoing_edges[order[i]]
            if F[destination, F_index] <= 1.0e-9:
                pass
            else:
                if F[destination, F_index] - data >= -1.0e-9:
                    transmit_data = data
                else:
                    transmit_data = F[destination, F_index]
                Z[source, destination, F_index] = Z[source, destination, F_index] + transmit_data
                F[destination, F_index] = F[destination, F_index] - transmit_data
                next_outgoing = np.where(A[:, F_index] == 1)[0][0]
                if next_outgoing == destination:
                    data = data - transmit_data
                    T[destination, source] = T[destination, source] - transmit_data
                else:
                    restdata, F, T, Z = split_greedy(transmit_data, A, F, T, Z, source, destination, next_outgoing)
                    Z[source, destination, F_index] = Z[source, destination, F_index] - restdata
                    F[destination, F_index] = F[destination, F_index] + restdata
                    data = data - transmit_data + restdata
                    T[destination, source] = T[destination, source] - transmit_data + restdata
            i = i + 1
    else:
        pass
        # print('no_finish_5: dead end')

    return (data, F, T, Z)


def solve_proportional(A, F):
    n = np.shape(A)[0]
    m = np.shape(A)[1]
    T = - np.dot(F, A.T)
    Z = np.zeros((n, n, m))
    step2_start = time.time()
    for j in range(n):
        for i in range(n):
            if j != i:
                F, T, Z = split_proportional(T[i,j], A, F, T, Z, j, i, j)

    step2_end = time.time()

    return (Z, step2_end - step2_start)


def split_proportional(data, A, F, T, Z, source, destination, outgoing):
    outgoing_edges = np.intersect1d(np.where(A[outgoing] == -1)[0], np.where(F[destination] > 1.0e-9)[0])
    if len(outgoing_edges) > 0:
        transmit_data = F[destination, outgoing_edges] * data / np.sum(F[destination, outgoing_edges])
        Z[source, destination, outgoing_edges] = Z[source, destination, outgoing_edges] + transmit_data
        F[destination, outgoing_edges] = F[destination, outgoing_edges] - transmit_data
        for i in range(np.shape(transmit_data)[0]):
            next_outgoing = np.where(A[:, outgoing_edges[i]] == 1)[0][0]
            if next_outgoing == destination:
                T[destination, source] = T[destination, source] - transmit_data[i]
            else:
                F, T, Z = split_proportional(transmit_data[i], A, F, T, Z, source, destination, next_outgoing)
    return (F, T, Z)
