#!/usr/bin/python
#_*_encoding:utf-8_*_

import sys

num = int(sys.argv[1])

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

if '__main__' == __name__:

    lines = open("/tmp/orders.txt")

    orders = []
    for line in lines:
        orders.append(line.strip())

    nparts = divideNParts(len(orders), num)

    count = 0
    for part in nparts:
        partorders = orders[part[0]:part[1]]
        f = open('orders_'+str(count)+".txt","w")
        for o in partorders:
            f.write(o)
            f.write('\n')
        f.close()
        count+=1
