from math import log

MAP_FUNCTIONS_DICT = {
    "logFunc":{
        "name": "log(n)",
        "nameSuffix": "",
        "kwargs":{
            "times": "__variable_i"
        }
    },

    "nlognFunc":{
        "name": "nlog(n)",
        "nameSuffix": "",
        "kwargs":{
            "times": "__variable_i"
        }
    },

    "nSquarelognFunc":{
        "name": "(n^2)log(n)",
        "nameSuffix": "",
        "kwargs":{
            "times": "__variable_i"
        }
    },

    "npowFunc":{
        "name": "n^",
        "nameSuffix": "__variable_powerVal",
        "kwargs":{
            "times": "__variable_i",
            "powe": "__variable_powerVal",
        }
    },

    "nFunc":{
        "name": "n",
        "nameSuffix": "",
        "kwargs":{
            "times": "__variable_i",
        }
    },
}

def logFunc(n, **kwargs):
    return log(n) * kwargs["times"]

def nlognFunc(n, **kwargs):
    return (n * log(n)) * kwargs["times"]

def nSquarelognFunc(n, **kwargs):
    return ( (n**2) *log(n) ) * kwargs["times"]

def npowFunc(n, **kwargs):
    return (n ** kwargs["powe"]) * kwargs["times"]

def nFunc(n, **kwargs):
    return kwargs["times"] * n