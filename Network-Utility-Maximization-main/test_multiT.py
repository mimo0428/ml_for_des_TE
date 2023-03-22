import multiprocessing as mp
def  working(i):
   print('Working process:%s' %i)
if __name__ == '__main__':
  ProcessWorker = []
  for i in range(12):
     p = mp.Process(target=working,args=(i,))
     ProcessWorker.append(p)
     p.start()
     p.join()
