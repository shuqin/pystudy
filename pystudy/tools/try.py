
from multitasks import *

def g(x):
    return x+1


def h():
    return taskPool.map(g, [1,2,3,4])


if __name__ == '__main__':

    taskPool = Pool(2) 
    print h()
    
    taskPool.close()
    taskPool.join()    
