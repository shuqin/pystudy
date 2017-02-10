
def outer():
    def inner():
        count = [1]
        print('inner: %d' % count[0])
        count[0] += 1
    return inner

def outer2():
    count = [1]
    def inner2():
        print('inner2: %d' % count[0])
        count[0] += 1
    return inner2

def outer3(alist):
    inners = []
    for e in alist:
        def inner3():
            print('inner3: %s' % e)
        inners.append(inner3)
    return inners 

def outer4(alist):
    inners = []
    for e in alist:
        def inner4(g):
            def inner():
                print('inner4: %s' % g)
            return inner
        inners.append(inner4(e))
    return inners

def p(alist,m):
    return sum(map(lambda x: x**m, alist))

def pclosure(alist, m):
    if m:
        return lambda l: sum(map(lambda x: x**m, l))
    if alist:
        return lambda n: sum(map(lambda x: x**n, alist))
    return lambda l,n: sum(map(lambda x: x**n, l))

def getlist(n):
    return map(lambda x:x+1, range(n))

if __name__ == '__main__':
    inner = outer()
    inner()
    inner()
    inner2 = outer2()
    inner2()
    inner2()

    for outer in [outer3, outer4]:
        inners = outer([1,2,3])
        for inner in inners:
            inner()

    alist = getlist(3)
    print('sum([1-3]^1) = ', p(alist, 1))
    print('sum([1-3]^2) = ', p(alist, 2))
    print('sum([1-3]^3) = ', p(alist, 3))
    
    msum = pclosure([], 1)
    print('sum([1-3]^1) = ', msum(getlist(3)))
    print('sum([1-5]^1) = ', msum(getlist(5)))
    
    msum = pclosure([], 2)
    print('sum([1-3]^2) = ', msum(getlist(3)))
    print('sum([1-5]^2) = ', msum(getlist(5)))
        
    mpower = pclosure(getlist(10), None)
    print('sum([1-10]^1) = ', mpower(1))
    print('sum([1-10]^3) = ', mpower(3))    

    plain = pclosure(None, None)
    print('sum([1-8]^1) = ', plain(getlist(8), 1))
    print('sum([1-8]^2) = ', plain(getlist(8), 2))
