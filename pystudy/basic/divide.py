#!/usr/bin/python
#_*_encoding:utf-8_*_

###########################
# 1 3
# 1 2
# 2 3
# converted to
# map[3=>[1,2], 2=>[1]] 
##########################

def read():
    inf = open('/tmp/data.txt')
    f2_f1_map = {}
    count = 0
    for line in inf:
        count += 1
        (f1, f2) = line.split()
        f1 = f1.strip()
        f2 = f2.strip()
        if not f2_f1_map.get(f2):
            f2_f1_map[f2] = []
        f2_f1_map[f2].append(f1)
    inf.close()
    return (f2_f1_map, count)

def divide(alist, unit=30):
    number = len(alist)
    if number <= unit:
        return [alist]

    start = 0
    alistList = []
    while start < number :
        end = start + unit
        alistPart = alist[start:end]
        alistList.append(alistPart)
        start += unit
    return alistList

def writeResult(f2_f1_map, count, unit=30):

    ouf = open('/tmp/out.txt', 'w')
    total = 0
    for (f2, alist) in f2_f1_map.iteritems():
        alistList = divide(alist)
        for alistPart in alistList:
            total += len(alistPart)
            info = "%s;%s\n" % (f2, ','.join(alistPart))
            ouf.write(info)
    ouf.close()

    print('lines in file: %s\n' % count)
    print('items in map: %s\n')
    assert count == total


if __name__ == '__main__':
    (f2_f1_map, count) = read()
    writeResult(f2_f1_map, count)
