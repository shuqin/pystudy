from multiprocessing import Pool
from common import catchExc

def f(x):
    return x+1

@catchExc
def g(x):
    return x*x

if __name__ == '__main__':

    taskpool = Pool(2)
    print(taskpool.map(f, [1,2,3]))
    # print taskpool.map(g, [1,2,3])   # decoratored func not allowed
    # print taskpool.map(lambda x: x*2, [1,2,3])  # lambda not allowed
