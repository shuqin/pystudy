

def divideNParts(total, N):
    '''
       divide [0, total) into N parts:
        return [(0, total/N), (total/N, 2M/N), ((N-1)*total/N, total)]
    '''

    each = total / N
    parts = []
    for index in range(N):
        begin = index*each
        if index == N-1:
            end = total
        else:
            end = begin + each
        parts.append((begin, end))
    return parts

class TaskProcessPool(func):
    def __init__(self):
        self.taskPool = Pool(processes=ncpus)
        self.func = func

    def addDownloadTask(self, func, entryUrls):
        self.taskPool.map_async(func, entryUrls)

    def close(self):
        self.taskPool.close()

    def join(self):
        self.taskPool.join()
