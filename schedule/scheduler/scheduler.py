
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')
import numpy as np
from schedule.KM import KM

class sheduler:
    def __init__(self, ):
        pass

    def shedule(job):
        ip = None
        GPU_id = None
        MIG = None
        return ip,  GPU_id, MIG
    

def binomial_matching(Net):
    net = np.array(Net)
    km = KM()
    max_ = km.compute(net.copy())
    return max_


    