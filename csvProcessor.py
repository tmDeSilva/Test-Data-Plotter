def processData(pFilename):
    grid = [line.strip().split(',') for line in open(pFilename, 'r').readlines()]
    keys = grid[0]
    grid = [[grid[i][j] for i in range(1,len(grid))] for j in range(len(grid[0]))]

    dicto = {}
    for i in range(len(grid)):
        if keys[i] != "TimeStamp":
            dicto[keys[i]] = [float(j) for j in grid[i]]

    T = dicto["TimeStep"]
    return (T,dicto,keys[2:])


def mergeDict(pDict1, pDict2):
    pDict = {}
    for key in pDict1.keys():
        if key == "TimeStep":
            pDict[key] = pDict1[key] + [pDict1[key][-1] + i for i in pDict2[key]]
        else:
            pDict[key] = pDict1[key] + pDict2[key]
    return pDict

    

def pad(pLength,pNumber,pChar = "0"):
    return pChar * (pLength - len(str(pNumber))) + str(pNumber)

def getKeys(pFilename):
    return open(pFilename, 'r').readlines()[0].strip().split(',')[2:]
