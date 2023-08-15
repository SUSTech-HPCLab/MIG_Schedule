
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')
import numpy as np
from schedule.KM import KM
from jobs.profile.standardized_throughput import job
import util.util


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
    result = []
    for i in max_:
        result.append(i[1])
    return result


def muxflow():
    pass





    