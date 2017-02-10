import random
import sys   
sys.setrecursionlimit(10000)

UPLIMIT = 10000
NUMBERS = 500
NUMBER_RANGE = (1,UPLIMIT/4)


def randNums(n):
    return [randGen(NUMBER_RANGE[0], NUMBER_RANGE[1]) for i in range(n)]

def randGen(start, end):
    return random.randint(start, end)

def solve(numlist):
    if UPLIMIT >= 1000 and NUMBERS >= 500:
        (finalResults, unMatchedNums) = baseSolve(numlist, matchSumUnrec)
    else:
        (finalResults, unMatchedNums) = baseSolve(numlist, matchSum)
    improve(finalResults, unMatchedNums)
    return (finalResults, unMatchedNums)

def baseSolve(numlist, matchSum):    
    if not numlist or len(numlist) == 0:
       return ([],[]);
    finalResults = []
    unMatchNums = []
    while len(numlist) > 0: 
        num = numlist.pop()
        matched = []
        if matchSum(UPLIMIT-num, numlist, matched):
            removelist(numlist, matched)
            matched.append(num)        
            finalResults.append(matched)
        else:
            unMatchNums.append(num)

    return (finalResults, unMatchNums)       

def removelist(origin, toberemoved):
    for e in toberemoved:
        if e in origin:
           origin.remove(e)

def copylist(numlist):
    return [num for num in numlist]

def matchSum(rest, restlist, prematched):
        
    if rest > 0 and len(restlist) == 0:
        return False

    if rest > 0 and len(restlist) == 1 and restlist[0] != rest:
        return False

    if rest > 0 and len(restlist) == 1 and restlist[0] == rest:
        prematched.append(restlist[0])
        return True

    getone = restlist[0]
    if rest > getone:
        prematched.append(getone)
        if matchSum(rest-getone, restlist[1:], prematched):
            return True
        else:
            prematched.remove(getone)
            return matchSum(rest, restlist[1:], prematched)
    elif rest == getone:
        prematched.append(getone)
        return True;
    else:
        return matchSum(rest, restlist[1:], prematched)


def matchSumUnrec(asum, sortedlist, matched):
    
    if asum > 0 and len(sortedlist) == 0:
        return False

    if asum > 0 and len(sortedlist) == 1 and sortedlist[0] != asum:
        return False

    outerInd = 0
    outersize = len(sortedlist)
    while outerInd < outersize:
        ind = outerInd
        size = len(sortedlist)
        rest = asum
        while ind < size:
            num = sortedlist[ind]
            if num < rest:
                matched.append(num)
                rest -= num
                ind += 1
            elif num == rest:
                matched.append(num)
                return True
            else:
                ind += 1
                continue

        # if not found in inner loop, then first elem is not included in solution.    
        outerInd += 1
        sortedlist = sortedlist[1:]
        del matched[:]

    return False
    

def improve(finalResults, unMatchedNums):
    for comb in finalResults:
        for num in comb:
            matched = []
            if matchSum(num, unMatchedNums, matched) and len(matched) > 1:
                print 'Improved: ' , num, ' ', matched
                comb.remove(num)
                comb.extend(matched)
                unMatchedNums.append(num)
                for e in matched:
                    unMatchedNums.remove(e)
                if len(unMatchedNums) == 0:
                    return

def printResult(finalResults, unMatchedNums, numlist):
    
    f_res = open('/tmp/res.txt', 'w')
    f_res.write('origin: ' + str(numlist) + '\n')
    f_res.write('averag: ' + str((float(sum(numlist))/len(numlist))) + '\n')
    f_res.write('solution: ')
    
    usedNums = 0
    finalNumList = []
    for comb in finalResults:
        f_res.write(str(comb) + ' ')
        assert sum(comb) == UPLIMIT
        usedNums += len(comb)
        finalNumList.extend(comb)
    finalNumList.extend(unMatchedNums)
    f_res.write('\nUnMatched Numbers: ' + str(unMatchedNums) + '\n')
    f_res.write('Used numbers: %s, UnMatched numbers: %d.\n' % (usedNums, len(unMatchedNums)))

    f_res.write('origin: %d , final: %d\n' % (len(numlist), len(finalNumList)))
    for e in finalNumList:
        numlist.remove(e)
    if len(numlist) > 0:
        f_res.write('Not Occurred numbers: ' + str(numlist))
    
    f_res.close() 


def to100(numlist):
  
    newnumlist = copylist(numlist)
    (finalResults, unMatchedNums) = solve(newnumlist)

    newnumlist = copylist(numlist)
    printResult(finalResults, unMatchedNums, newnumlist)

if __name__ == '__main__':
    to100(randNums(NUMBERS))

