import math

def findRoot(g, x, a, b, epsilon):
    m = (a+b)/2
    f = eval('lambda x : ' + g)
    if ( (f(a)*f(b) < 0) and math.fabs(b-a) > epsilon):
        if (f(a)*f(m) < 0):
            m = findRoot(g, x, a, m, epsilon)
        else:
            m = findRoot(g, x, m, b, epsilon)

    return m


def findAllRoots(g, x, a, b, epsilon):
    lijst = [[a,b]]

    f = eval('lambda x : ' + g)
    
    while(numRoots(lijst) < 4 and (lijst[0][1] - lijst[0][0]) > epsilon):
        lijst = halveerIntervallen(lijst)

    roots= []
    for j in lijst:
        if f(float(j[0]))*f(float(j[1])) < 0 :
            roots.append(findRoot(g, x, j[0], j[1], epsilon))
    roots.sort()
    return roots
            
    
        
def numRoots(lijst):
    j = 0
    for i in lijst:
        if i[0]*i[1] < 1 :
            j += 1
    return j
        
          


def halveerIntervallen(lijst):
    hoi = []
    for i in lijst:
        m = (i[1] + i[0])/2
        hoi.extend(([i[0], m], [i[1], m]))
    return hoi
