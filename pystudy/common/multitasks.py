from multiprocessing import (cpu_count, Pool)
from multiprocessing.dummy import Pool as ThreadPool

ncpus = cpu_count()



def divideNParts(total, N):
    '''
       divide [0, total) into N parts:
        return [(0, total/N), (total/N, 2M/N), ((N-1)*total/N, total)]
    '''

    each = total / N
    parts = []
    for index in range(N):
        begin = index * each
        if index == N - 1:
            end = total
        else:
            end = begin + each
        parts.append((begin, end))
    return parts


class IoTaskThreadPool(object):
    '''
       thread pool for io operations
    '''
    def __init__(self, poolsize):
        self.ioPool = ThreadPool(poolsize)

    def exec(self, ioFunc, ioParams):
        if not ioParams or len(ioParams) == 0:
            return []
        return self.ioPool.map(ioFunc, ioParams)

    def execAsync(self, ioFunc, ioParams):
        if not ioParams or len(ioParams) == 0:
            return []
        self.ioPool.map_async(ioFunc, ioParams)

    def close(self):
        self.ioPool.close()

    def join(self):
        self.ioPool.join()

