import math

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
from matplotlib.ticker import *

df = pd.read_excel('./result/res_solver_ncflow.xlsx', sheet_name='time')
# df = pd.read_excel('./result/res_solver_0_part.xlsx', sheet_name='time')

df.drop(df.head(2).index,inplace=True)

colors1 = ['navy', 'blue', 'royalblue', 'cornflowerblue']
colors2 = ['red', 'orangered', 'coral', 'salmon']
colors3 = 'slategray'

plt.plot(df['topology'], df['all_original_gurobi'], label='all_original_gurobi', c=colors1[3], marker='x')
plt.plot(df['topology'], df['all_des_gurobi'], label='all_des_gurobi', c=colors1[2], marker='s')
plt.plot(df['topology'], df['reduced_original_gurobi'], label='reduced_original_gurobi', c=colors2[3], marker='x')
plt.plot(df['topology'], df['reduced_des_gurobi'], label='reduced_des_gurobi', c=colors2[1], marker='s')
plt.plot(df['topology'], df['ncflow'], label='ncflow', c=colors3, marker='o')

plt.ylabel('Time (s)')
plt.yscale('log')

plt.legend()
plt.savefig('./result/gurobi_ncflow.png')
# plt.savefig('./result/gurobi_part.png')

