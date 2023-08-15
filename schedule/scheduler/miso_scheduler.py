
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')

import numpy as np
from itertools import permutations
from schedule.KM import KM
from jobs.profile.standardized_throughput import job
import util.util
path = '/home/zbw/MIG/MIG_Schedule/jobs/profile/single_standardlized'
job_list = []
with open(path, 'r') as f:
    for line in f:
        line = line.strip()
        lines = line.split(" ")
        job_list.append(lines)
f.close()



config_map = {7:"1c-7g-80gb", 4:"1c-4g-40gb", 3:"1c-3g-40gb", 2:"1c-2g-20gb", 1:"1c-1g-10gb"}
class sheduler:
    def __init__(self, ):
        pass

    def shedule(job):
        ip = None
        GPU_id = None
        MIG = None
        return ip,  GPU_id, MIG
    


def miso(online_jobs, online_jobs_qos, offline_jobs):
    GPU_list = []
    for i in GPU_list:
        GPU_list[i] = []




    # for i in offline_jobs:
    #     index = get_min(GPU_list)
    #     GPU_list[index].append(i)


def get_min(GPU_list):
    index = 0
    min = 999
    for i in GPU_list:
        if len(GPU_list[i]) <= min:
            min = len(GPU_list[i])
            index = i
    
    return index

def miso_partition_optimizer(online_jobs , offline_jobs):
    online_config = []
    for i in online_jobs:
        online_config.append(best_fit(i))
    

    configs = util.util.get_MIG_config()
    valid_config = []


    for i in configs:
        valid = True
        if len(i) == len(online_jobs) + len(offline_jobs):
            for j in online_config:
                if j not in i:
                    valid = False
                    break
            if valid:
                valid_config.append(i)
    
    for i in valid_config:
        remaining_list = i
        for j in online_config:
            remaining_list.remove(j)

    array = remaining_list
    all_permutations = permutations(array)

    best_obj = 0
    best_config = None

    for permutation in all_permutations:
        config = []
        for i in  permutation:
            config.append(config_map.get(i))
        throught =  Calculated_throughput(config, offline_jobs)
        if throught > best_obj:
            best_config = config




def best_fit(online_job):
    MIG_partition = None
    return MIG_partition


def Calculated_throughput(config_list, jobs):
    throughput = 0
    global job_list

    for i in job_list:
        for j in range(0, len(jobs)):
            if jobs[j][0] == i[0] and jobs[j][1] == i[1] and config_list[j] == i[2]:
                throughput = throughput + float(i[3])
    

    return throughput
        


# miso()

# array = [[1,2,3],[4,5,6]]

# # 生成所有排列组合可能
# all_permutations = permutations(array)

# # 打印所有排列组合
# for permutation in all_permutations:
#     print(permutation)

# print(array.index([1,2,3]))
print(Calculated_throughput (['1c-4g-40gb', '1c-3g-40gb'], [['vgg19','32'],['vgg19','32']]))