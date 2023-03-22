import numpy as np 
import matplotlib.pyplot as plt

def draw_hist(T):
    hist_data = np.sort(T.flatten())
    hist_data = hist_data[np.where(hist_data > 0)[0]]
    
    bins = np.arange(0, 100, 2)
    plt.hist(hist_data, bins, density = True)
    plt.ylim((0, 0.15))
    
    plt.show()
    return


def draw_log_hist(T):
    hist_data = np.sort(T.flatten())
    hist_data = hist_data[np.where(hist_data > 0)[0]]
    
    hist_data = np.log10(hist_data)
    
    bins = np.arange(0, 2, 0.04)
    plt.hist(hist_data, bins, density = True)
    plt.ylim((0, 3.0))

    plt.show()
    return


def draw_heatmap(T):
    '''for i in range(np.shape(T)[0]):
        T[i,i] = 0'''
    # T = np.power(T, 1-0.7) / (1 - 0.7)
    fig, ax = plt.subplots()
    im = ax.imshow(T, cmap="Blues", vmin = 0, vmax = 120)
    for i in range(np.shape(T)[0]):
        for j in range(np.shape(T)[1]):
            text = ax.text(j, i, np.around(T[i, j],1), ha="center", va="center", color="k")
    plt.colorbar(im)
    plt.show()
    return