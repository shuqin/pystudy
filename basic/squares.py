
def square2(n):
    return map(lambda x, y: x*x+y, [x for x in range(n)],
                                   [2*x+1 for x in range(n)])    


def square(n):
    '''
      cal square of [1-n]
    '''
    sq_init = 0
    sq_diff = 1
    f = open('squares.txt', 'w')
    the_range = [x+1 for x in range(n)]
    for num in the_range: 
        sq_res = sq_init + sq_diff
        sq_init = sq_res
        sq_diff += 2
        f.write('%d*%d=%d\n' % (num, num, sq_res))
    f.close()

if __name__ == '__main__':
    #square(1000000)
    sq_result = square2(1000000)
    with open('squares.txt', 'w') as f:
        f.writelines("%s*%s=%s\n" % (ind+1, ind+1, sq_result[ind])
                                  for ind in range(len(sq_result)))
