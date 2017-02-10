import pp
from multiprocessing import Process, Pool, Pipe

def addNFunc(n):
    return lambda x:x+n

def fac(n):
    if n <= 1:
        return 1
    return reduce(lambda x,y: x*y, map(addNFunc(1), range(n)))

def computingFacOfRange(begin, end):
    for i in map(addNFunc(begin), range(end-begin+1)):
        print i, '! =', fac(i)

def another():
    print 'another quick job'

def  QuadraticSum(n, m):
    ''' compute 1^m + 2^m + ... + n^m '''
    if n <= 1:
        return 1
    return reduce(lambda x,y: x+y**m, map(addNFunc(1), range(n)))

def expressQS(n,m):
    if n <= 1:
        return '1'
    return reduce(lambda x,y: "%s+%s" %(str(x),str(y)+'^'+str(m)), map(addNFunc(1), range(n)))

def obtainQuadraticSum(n, m):
    return "%s=%s" % (expressQS(n, m), QuadraticSum(n,m))

def obtainQuadraticSumByPipe(conn, n, m):
    conn.send(obtainQuadraticSum(n, m))

def printQuadraticSum(n, m):
    print obtainQuadraticSum(n, m)

def testQuadraticSum():
    for n in [1,2,3,4,5]:
        for m in [-1,1,2,3]:
            printQuadraticSum(n, m)

def usingPP():
    ''' using pp module for python concurrent programming '''
    nworkers = 10
    ppservers = ()
    job_server = pp.Server(nworkers, ppservers=ppservers)

    print "Starting pp with", job_server.get_ncpus(), "workers"

    jobs = []
    for i in range(nworkers):
        jobs.append(job_server.submit(computingFacOfRange, (i*10+1, (i+1)*10), (fac,addNFunc,)))

    jobs.append(job_server.submit(another, ()))

    for job in jobs:
        job()

    job_server.print_stats()


def usingMultiprocess():
    ''' using multiprocessing module for python concurrent programming '''
    num = 100
    processes = []

    print '************ using original process ***********'
    input_conn, output_conn = Pipe()
    for m in [-1,1,2,3]:
        p = Process(target=obtainQuadraticSumByPipe, args=(input_conn, num,m,))
        p.start()
        print output_conn.recv()

    print '------------- using Pool -------------'
    pool = Pool(processes=4)
    for m in [-1,1,2,3]:
        pool.apply(printQuadraticSum, (num,m))


if __name__ == '__main__':
    testQuadraticSum()
    usingPP()
    usingMultiprocess()
