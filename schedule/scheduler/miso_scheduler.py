
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')

import numpy as np
import queue
import util.util

from itertools import permutations
from itertools import combinations
from jobs.profile.standardized_throughput import get_job_list


path = '/home/zbw/MIG/MIG_Schedule/jobs/profile/single_standardlized'
job_list = []
with open(path, 'r') as f:
    for line in f:
        line = line.strip()
        lines = line.split(" ")
        job_list.append(lines)
f.close()


online_job_list = get_job_list()

class online_job:
    def __init__(self, model_name, batch_Size, qos):
        self.model_name = model_name
        self.batch_Size = batch_Size
        self.qos = qos
    def __str__(self):
        return f"online Model Name: {self.model_name}  Batch Size: {self.batch_Size}"

class offline_job:
    def __init__(self, model_name, batch_Size, epoch):
        self.model_name = model_name
        self.batch_Size = batch_Size
        self.epoch = epoch
    
    def __str__(self):
        return f"offline Model Name: {self.model_name} Batch Size: {self.batch_Size}"

config_map = {7:"1c-7g-80gb", 4:"1c-4g-40gb", 3:"1c-3g-40gb", 2:"1c-2g-20gb", 1:"1c-1g-10gb"}

reverser_map = {"1c-7g-80gb" : 7, "1c-4g-40gb": 4, "1c-3g-40gb":3, "1c-2g-20gb":2, "1c-1g-10gb":1, "baseline":10}
class miso_sheduler:
    def __init__(self, GPU_list = [], max_job_per_GPU=3):
        self.GPU_list = GPU_list
        self.max_job_per_GPU = max_job_per_GPU
        self.online_job_queue = queue.Queue()
        self.offline_job_queue = queue.Queue()


    def miso_cluster(self, new_job):

        index_list = self.get_index_list(self.GPU_list)
        job_num = len(self.GPU_list[index_list[0]])
        if job_num + 1 <= self.max_job_per_GPU:
          
            self.GPU_list[index_list[0]].append(new_job)
            if(not self.miso_partition_optimizer(self.GPU_list[index_list[0]])):
                self.GPU_list[index_list[0]].remove(new_job)
                if isinstance(new_job, online_job):
                    self.online_job_queue.put(new_job)
                else:
                    self.offline_job_queue.put(new_job)
        
        else:
            if isinstance(new_job, online_job):
                self.online_job_queue.put(new_job)
            else:
                self.offline_job_queue.put(new_job)

    def get_index_list(self, GPU_list):
        sorted_indices = sorted(range(len(GPU_list)), key=lambda i: len(GPU_list[i]))
        return sorted_indices
    
    
    def miso_partition_optimizer(self, jobs):
        online_jobs = []
        offline_jobs = []

        for i in jobs:
            if isinstance(i, online_job):
                online_jobs.append(i)
            else:
                offline_jobs.append(i)

        online_config = []

        for i in online_jobs:
            online_config.append(self.best_fit(i))
    
        configs = util.util.get_MIG_config()
        valid_config = []


        for i in configs:
            valid = True
            if len(i) >= len(online_jobs) + len(offline_jobs):
                for j in online_config:
                    if j not in i:
                        valid = False
                        break
                if valid:
                    valid_config.append(i.copy())

        if len(valid_config) == 0:
            return False


        for i in valid_config:
            for j in online_config:
                i.remove(j)

        print(valid_config)
        best_obj = 0
        best_config = None
        for i in valid_config:
            n = len(offline_jobs)
            if n == 0 :
                return True
            
            all_combinations = list(combinations(i, n))
            for combo in all_combinations:
                config = []
                for z in combo:
                    config.append(config_map.get(z))
                throught =  self.Calculated_throughput(config, offline_jobs)
                if throught > best_obj:
                    best_config = config
                    best_obj = throught
        print(best_obj)
        print(best_config)
        for i in offline_jobs:
            print(i)
        return True
                


   
    def Calculated_throughput(self, config_list, jobs):
        throughput = 0
        global job_list

        for i in job_list:
            for j in range(0, len(jobs)):
                if jobs[j].model_name == i[0] and jobs[j].batch_Size == i[1] and config_list[j] == i[2]:
                    throughput = throughput + float(i[3])
    

        return throughput
    
    def best_fit(self, online_job):
        global online_job_list
        MIG_partition_list = []
        for i in online_job_list:
            if i.model_name == online_job.model_name and int(i.batch_Size)== int(online_job.batch_Size) and float(i.tail) < online_job.qos:
                MIG_partition_list.append(i.config)


        min = 100
        for i in range(0, len(MIG_partition_list)):
            GI = reverser_map[MIG_partition_list[i]]
            if GI:
                if GI <= min:
                    min = GI

        return min



test1  = online_job('resnet152', '16' , 80)
test2  = offline_job('resnet152', '8' , 800)
test3  = offline_job('resnet50', '16' , 800)
test4 = offline_job("bert", "8", 800)
jobs = [test1]
GPU_list = [[]]
test = miso_sheduler(GPU_list=GPU_list)

test.miso_cluster(test1)
test.miso_cluster(test2)
print(test.GPU_list)
test.miso_cluster(test4)
# test.miso_cluster(test2)
# test.miso_partition_optimizer(jobs)
# print(test.best_fit(test1))



        
