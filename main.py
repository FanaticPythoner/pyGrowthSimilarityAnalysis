import pandas as pd
import cupy as np
import matplotlib.pyplot as plt
from math import log
from TestFunctions import MAP_FUNCTIONS_DICT, logFunc, nlognFunc, nSquarelognFunc, npowFunc, nFunc
from threading import Thread


# Total number of times to call each test function
TOTAL_ITER = 100000

# The step size between each C constant try
C_STEP = 0.5

# Test the C constant until this value
C_MAX_VALUE = 100

# Maximum number of most probable test functions to keep in the plot
KEEP_TOP_PLOT = 5

# When the distance between the two functions grows when boosting the C value,
# wait X iterations before breaking the loop
TRESHOLD_BREAK_C = 25

# When the distance between the two functions grows, wait X iterations before breaking the loop
TRESHOLD_BREAK = 1000



# ====================================================
# This is the main function you want to test

def baselineFunction(n, **kwargs):
    return ( (4*(n**3)) + (n**2)*log(n+1) +1 ) / ( 2*n+3 )



class ThreadRet(Thread):
    """
        Thread class implementation that return a value
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return



def getDistance(y1, x1, y2, x2):
    """
        Get the average distance between two function

        Parameters:
            1. originalArr : Array of Y values of the baselineFunction
            2. arr2        : Array of Y values of the test function

        RETURN -> Float: dist
    """
    res = np.sqrt( np.power((x1-x2), 2) + np.power((y1-y2), 2) )
    res = np.asnumpy(res).tolist()
    return res


def getArrFunc(originalArr, funcCallable, dictKwargs, isOriginal=False):
    """
        Get the array of Y values from a given test function and the 
        average absolute distance in float between the original and callable function

        Parameters:
            1. originalArr  : Array of Y values of the baselineFunction
            2. funcCallable : Function to test
            3. dictKwargs   : Dict to pass as **kwargs for the funcCallable

        RETURN -> [List: arr2, Float: dist]
    """
    arr2 = []
    currThreshold = 0
    prev = None
    sumDist = 0
    distCount = 0

    for i in range(1, TOTAL_ITER):
        res = [funcCallable(i, **dictKwargs), i]
        arr2.append(res)
        y1, x1 = originalArr[i - 1]
        y2, x2 = arr2[i - 1]
        valCurr = getDistance(y1, x1, y2, x2)

        if prev is None:
            prev = valCurr
        else:
            diff = valCurr - prev
            if diff > 0:
                currThreshold = currThreshold + 1
                if currThreshold == TRESHOLD_BREAK:
                    break
            else:
                currThreshold = 0

            prev = valCurr
            sumDist = sumDist + valCurr
            distCount = distCount + 1

    dist = sumDist / distCount

    return [[x[0] for x in arr2], dist, [originalArr, arr2, funcCallable, dictKwargs]]


def getTestFunctionLoop(key, loopValKey, **kwargs):
    """
        Get the parameters for a given test function

        Parameters:
            1. key        : Key of the function in the MAP_FUNCTIONS_DICT
            2. loopValKey : Key of the loop variable in the **kwargs dict

        RETURN -> [Callable: funcCallable, Dict: dictKwargs, Str: name]
    """
    variableSplit = "__variable_"
    funcCallable = globals()[key]
    objFunc = MAP_FUNCTIONS_DICT[key]

    name = objFunc["name"]

    if "nameSuffix" in objFunc:
        suff = objFunc["nameSuffix"]
        if suff.startswith(variableSplit):
            suffVarKey = suff.split(variableSplit)[-1]
            suff = str(kwargs[suffVarKey])
        name = name + suff

    name = name + " * " + str(kwargs[loopValKey])

    dictKwargs = {}

    for keyK, valK in objFunc["kwargs"].items():
        if valK.startswith(variableSplit):
            valKVarKey = valK.split(variableSplit)[-1]
            valK = kwargs[valKVarKey]

        dictKwargs[keyK] = valK

    return [funcCallable, dictKwargs, name]


def getBaselineArr():
    """
        Get the baseline function Y values array

        RETURN -> [arr]
    """
    arr = []
    for i in range(1, TOTAL_ITER):
        res = baselineFunction(i)
        arr.append([res, i])
    return arr


def arrToDataFrame(arrVals, arr):
    """
        Get a DataFrame object from the list of Y values found

        Parameters:
            1. arrVals: List of Y values found

        RETURN -> DataFrame: df
    """
    dic = {}
    for val in arrVals:
        name = val[-2]

        if (name.startswith('n_')):
            if (name.split('n_')[1] == '1.0'):
                continue

        if (name.startswith('npow_')):
            if (name.split('npow_')[1] == '1.0'):
                continue

        dic[name] = val[0]

    df = pd.DataFrame(dic)

    df.insert(loc=0, column='original', value=[x[0] for x in arr])
    return df


def filterFoundValues(arrVals):
    """
        Get the filtered Y values found

        Parameters:
            1. arrVals: List of Y values found

        RETURN -> [arrVals]
    """
    arrVals = [x for x in arrVals if len(
        x[0]) > 2 and type(x[0][0]) != type('')]

    arrVals = sorted(arrVals, key=lambda tup: abs((tup[1])))
    arrValsTmp = []
    for i in range(len(arrVals)):
        if len(arrValsTmp) == KEEP_TOP_PLOT:
            break

        arrValsTmp.append(arrVals[i])

    return arrValsTmp


def threadInnerFuncTreatment(arr, nameFunc, iName, kwargs):
    """
        Thread inner function that get the array of value points
        from a given test function
    
        Parameters:
            1. arr      : Array of Y values of the baselineFunction
            2. nameFunc : Name of the test function
            3. iName    : loop variable name (i)
            4. kwargs   : List of parameters to pass to the test function as **kwargs

        RETURN -> List: arrVals
    """
    arrVals = []
    itera = [x * C_STEP for x in range(1, int(C_MAX_VALUE/C_STEP))]
    currThreshold = 0
    prev = None

    for i in itera:
        kwargs[iName] = i
        funcCallable, dictKwargs, name = getTestFunctionLoop(nameFunc, iName, **kwargs)
        valCurr = getArrFunc(arr, funcCallable, dictKwargs) + [name] + [i]
        arrVals.append(valCurr)

        if prev is None:
            prev = valCurr
        else:
            valCurr, prev = reshapeAll([valCurr, prev])
            diff = np.array(valCurr[0]) - np.array(prev[0])
            diff = np.sum(diff) / len(diff)
            diff = np.asnumpy(diff).tolist()
            if diff > 0:
                currThreshold = currThreshold + 1
                if currThreshold == TRESHOLD_BREAK_C:
                    break
            else:
                currThreshold = 0

            prev = valCurr

    return arrVals


def reshapeAll(arrVals):
    """
        Reshape all sub array of Y values to be the same size
    
        RETURN -> arrVals
    """
    minShape = min([len(x[0]) for x in arrVals])

    for iVal in range(len(arrVals)):
        currItem = arrVals[iVal]
        diff = minShape - len(currItem[0])
        lastEl = currItem[0][-1]

        if diff > 0:
            for i in range(diff):
                arrVals[iVal][0] = arrVals[iVal][0] + [lastEl]
        elif diff < 0:
            arrVals[iVal][0] = arrVals[iVal][0][:diff]

    return arrVals
    


def getFuncs(arr):
    """
        Get the test functions for a given iteration in the main loop

        Parameters:
            1. arr : Y values of the baseline function

        RETURN -> [List: arr, List: arrVals]
    """
    allTestFunctionsParam = [
        ("logFunc", "i", {
            "i": None
        }),

        ("nlognFunc", "i", {
            "i": None
        }),

        ("npowFunc", "i", {
            "i": None,
            "powerVal": 2
        }),

        ("npowFunc", "i", {
            "i": None,
            "powerVal": 3
        }),

        ("nSquarelognFunc", "i", {
            "i": None
        }),

        ("nFunc", "i", {
            "i": None
        }),        
    ]

    threadsDict = {}
    for index, (name, iName, kwargs) in enumerate(allTestFunctionsParam):
        threadsDict[name + "_" + str(index)] = ThreadRet(target=threadInnerFuncTreatment, args=(arr, name, iName, kwargs))
        threadsDict[name + "_" + str(index)].start()

    arrVals = []
    for key, val in threadsDict.items():
        arrVals = arrVals + threadsDict[key].join()


    return [arr, arrVals]


if __name__ == "__main__":
    arr = getBaselineArr()
    arr, arrVals = getFuncs(arr)

    arrVals = filterFoundValues(arrVals)

    arrVals = reshapeAll(arrVals)
    minShape = min([len(x[0]) for x in arrVals])
    diff = minShape - len(arr)
    if diff < 0:
        arr = arr[:diff]
    
    df = arrToDataFrame(arrVals, arr)

    df.plot()
    plt.show()
