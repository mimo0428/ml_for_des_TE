import pickle
import os
import numpy as np
import pandas as pd
from pandas import DataFrame
from Helper import get_satisfation
import argparse


parser = argparse.ArgumentParser(description='Test for argparse')
parser.add_argument('--capacity', '-c', help='set link capacity', required=True)
args = parser.parse_args()

cap = float(args.capacity)

file_ncflow = 'part_ncflow_'+ str(int(cap))
file_pf4 = 'part_PF4_' + str(int(cap))

file_path2 = './result/res_ncflow3_c_' + str(int(cap)) + '_all.xlsx'
# file_path1 = './result/res_ncflow3_c_1000.xlsx'


def setRamdom():
    network_list = ['Airtel', 'Gambia']
    Demand_list = []

    n = 16
    Demand=np.random.randint(0,10,size=[n,n])
    Demand_list.append(Demand)

    n = 28
    Demand=np.random.randint(0,10,size=[n,n])
    Demand_list.append(Demand)

    

    filename = ['Airtel1', 'Gambia1']
    

    return network_list, Demand_list, filename


def readpklDemand(i):
    # pklname = './demand/' + i 
    pklname = './small_demand/' + i 
    # pklname = './small_demand_add/' + i
    
    f = open(pklname,'rb')
    data = pickle.load(f)
    # print(data.shape)

    return data

def readname():
    # topoPath = './demand'
    topoPath = './small_demand'
    # topoPath = './small_demand_add'

    filename = os.listdir(topoPath)
    # print(filename)
    name = []
    Demand_list = []
    for i in filename:
        Demand = readpklDemand(i)
        portion = i.split('.')   #把文件名拆分为名字和后缀
        # if portion[1] == ".graphml":
        name.append(portion[0])
        Demand_list.append(Demand)
    # print(len(name))

    # print(name)
    return name, Demand_list, filename

def parse_filename(filename):
    portion = filename.split('_')
    # print(portion)
    problem = portion[0]
    traffic_seed = portion[2]
    scale_factor = portion[3]
    return problem, traffic_seed,scale_factor

def getNcflow(file_path2):
    
    data_time = pd.read_excel(file_path2, sheet_name = 'time',header = [0])
    data_value = pd.read_excel(file_path2, sheet_name = 'optimal_value',header = [0])
    data_satisfaction = pd.read_excel(file_path2, sheet_name = 'optimal_value',header = [0])
    
    data_time.set_index("filename", inplace=True)
    data_value.set_index("filename", inplace=True)
    data_satisfaction.set_index("filename", inplace=True)

    # print(data_time)
    
    for filename, row in data_time.iterrows():
        problem,traffic_seed,scale_factor = parse_filename(filename)
        nc_p_time, nctime, ncvalue, total_demand = getOneNcflow(problem,traffic_seed,scale_factor,0)
        # print(total_demand)
        # print("!!!")
        # print(nc_p_time)
        data_time.loc[filename,'ncflow_p'] = nc_p_time
        data_time.loc[filename,'ncflow'] = nctime
        data_value.loc[filename,'ncflow'] = ncvalue
        data_value.loc[filename,'total_demand'] = total_demand
        
        
        
        pf4time, pf4value = getOnePF4(problem,traffic_seed,scale_factor)
        # print(pf4value)
        data_time.loc[filename,'PF4'] = float(pf4time)
        data_value.loc[filename,'PF4'] = float(pf4value)
        
        # 计算 traffic demand
        orivalue = data_value.loc[filename,'all_original_gurobi']
        # print("!!!!!")
        # print(orivalue)
        desvalue = data_value.loc[filename,'all_des_gurobi']
        data_satisfaction.loc[filename,'all_original_gurobi'] = float(orivalue) / float(total_demand)
        data_satisfaction.loc[filename,'all_des_gurobi'] = float(desvalue) / float(total_demand)
        data_satisfaction.loc[filename,'ncflow'] = float(ncvalue) / float(total_demand)
        data_satisfaction.loc[filename,'PF4'] = float(pf4value) / float(total_demand)
        data_satisfaction.loc[filename,'total_demand'] = float(total_demand)
    
    data_time = data_time.sort_values(by="filename",ascending=True)
    data_value = data_value.sort_values(by="filename",ascending=True)
    data_satisfaction = data_satisfaction.sort_values(by="filename",ascending=True)
    
    data_time['filename'] = data_time.index
    data_value['filename'] = data_value.index
    data_satisfaction['filename'] = data_satisfaction.index
    
    
    
    excelWriter = pd.ExcelWriter(file_path2, engine='openpyxl') 
    DataFrame(data_time).to_excel(excel_writer=excelWriter, sheet_name='time', index=False, header=True)
    DataFrame(data_value).to_excel(excel_writer=excelWriter, sheet_name='optimal_value', index=False, header=True)
    DataFrame(data_satisfaction).to_excel(excel_writer=excelWriter, sheet_name='traffic_satisfaction', index=False, header=True)

    excelWriter.save()
    excelWriter.close()   



def getOneNcflow(problem,traffic_seed,scale_factor,iteration):
    path_ncflow = '../ncflow/data/' + file_ncflow + '.csv'
    data_all = pd.read_csv(path_ncflow, header = [0])
    # data_all = data_all.head()
    data_all.set_index(['problem', 'traffic_seed','scale_factor', 'iteration'],drop=False,inplace=True)
    
    t1 = 0
    t2 = 0
    t3 = 0
    for index, row in data_all.iterrows():
        if isinstance(index[1],int):
            # print("!!!")
            t1 = 1 
        if isinstance(index[2],float):
            # print("????")
            t2 = 1
        if isinstance(index[3],int):
            t3 = 1 
        break

    if t1 == 1:
        traffic_seed = int(traffic_seed)
    else:
        traffic_seed = str(traffic_seed)

    if t3 == 1:
        iteration = int(iteration)
    else:
        iteration = str(iteration)
    
    if t2 == 1:
        scale_factor = float(scale_factor)
    else:
        scale_factor = str(scale_factor)
    print(data_all.index)
    # print(data_all.loc[(str(problem),traffic_seed,iteration),'runtime'])
    ncflow_time = float(data_all.loc[(str(problem),traffic_seed,scale_factor,iteration),'runtime'])
    ncflow_p_time = float(data_all.loc[(str(problem),traffic_seed,scale_factor,iteration),'runtime'])+ float(data_all.loc[(str(problem),traffic_seed,scale_factor,iteration),'partition_runtime'])
    
    ncflow_value = float(data_all.loc[(str(problem),traffic_seed,scale_factor,iteration),'total_flow'])
    ncflow_demand = float(data_all.loc[(str(problem),traffic_seed,scale_factor,iteration),'total_demand'])
    return ncflow_p_time, ncflow_time, ncflow_value, ncflow_demand
    
def getOnePF4(problem,traffic_seed,scale_factor):
    path_pf4 = '../ncflow/data/' + file_pf4 + '.csv'
    data_all = pd.read_csv(path_pf4,header = [0])
    # data_all = data_all.head()
    data_all.set_index(['problem', 'traffic_seed','scale_factor'],drop=False,inplace=True)
    
    # print(data_all)
    
    # for index, row in data_all.iterrows():
    #     print(index)

    t1 = 0
    t3 = 0
    for index, row in data_all.iterrows():
        if isinstance(index[1],int):
            # print("!!!")
            t1 = 1 
        if isinstance(index[2],float):
            # print("!!!")
            t3 = 1 
        break

    if t1 == 1:
        traffic_seed = int(traffic_seed)
    else:
        traffic_seed = str(traffic_seed)
    if t3 == 1:
        scale_factor = float(scale_factor)
    else:
        scale_factor = str(scale_factor)

        
    pf4_time = data_all.loc[(problem,traffic_seed,scale_factor),'runtime']
    pf4_value = data_all.loc[(problem,traffic_seed,scale_factor),'total_flow']
    return pf4_time, pf4_value

if __name__=="__main__":

    
    getNcflow(file_path2)
    
    # filepkl = 'Ion.graphml_poisson_1168726174_128.0_1000.0_0.9_0.00026_traffic-matrix.pkl'
    # d = readpklDemand(filepkl)
    # print(d)