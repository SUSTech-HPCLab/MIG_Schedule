
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

config_map = {7:"1c-7g-80gb", 4:"1c-4g-40gb", 3:"1c-3g-40gb", 2:"1c-2g-20gb", 1:"1c-1g-10gb"}

reverser_map = {"1c-7g-80gb" : 7, "1c-4g-40gb": 4, "1c-3g-40gb":3, "1c-2g-20gb":2, "1c-1g-10gb":1, "baseline":10}

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
        self.submit_time = 0
        self.start_time = -1
        self.progress = 0
        self.end_time = None
        self.speed = 0
     
        
    
    def __str__(self):
        return f"offline Model Name: {self.model_name} Batch Size: {self.batch_Size} Start_time: {self.start_time}, End_time: {self.end_time} speed: {self.speed}"


class miso_sheduler:
    def __init__(self, GPU_list = [], max_job_per_GPU=7):
        self.GPU_list = GPU_list
        self.config_list = []
        self.max_job_per_GPU = max_job_per_GPU
        self.online_job_queue = queue.Queue()
        self.offline_job_queue = queue.Queue()
        self.throughput = []

        for i in range(0, len(GPU_list)):
            self.config_list.append([])
            self.throughput.append(0)


    def miso_cluster(self, new_job):

        index_list = self.get_index_list(self.GPU_list)
        job_num = len(self.GPU_list[index_list[0]])
        if job_num + 1 <= self.max_job_per_GPU:
          
            self.GPU_list[index_list[0]].append(new_job)
           
            if(not self.miso_partition_optimizer(self.GPU_list[index_list[0]], index_list[0])):
                self.GPU_list[index_list[0]].remove(new_job)
                if isinstance(new_job, online_job):
                    self.online_job_queue.put(new_job)
                else:
                    self.offline_job_queue.put(new_job)
                return False
            elif isinstance(new_job, offline_job):
                throught_put = self.miso_partition_optimizer(self.GPU_list[index_list[0]], index_list[0])
                if throught_put < self.throughput[index_list[0]]:
                    self.GPU_list[index_list[0]].remove(new_job)
                    self.miso_partition_optimizer(self.GPU_list[index_list[0]], index_list[0])
                    self.offline_job_queue.put(new_job)
                    return False
                else:
                    self.throughput[index_list[0]] = throught_put
            
            return True
        
        else:
            if isinstance(new_job, online_job):
                self.online_job_queue.put(new_job)
            else:
                self.offline_job_queue.put(new_job)
            return False
            

    def get_index_list(self, GPU_list):
        sorted_indices = sorted(range(len(GPU_list)), key=lambda i: len(GPU_list[i]))
        return sorted_indices
    
    
    def miso_partition_optimizer(self, jobs, index):
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
                tmp = i.copy()
                for j in online_config:
                    if j not in tmp:
                        valid = False
                        break
                    else:
                        tmp.remove(j)
                if valid:
                    valid_config.append(i.copy())

        if len(valid_config) == 0:
            return False

        for i in valid_config:
            for j in online_config:
                i.remove(j)

        
        best_obj = 0
        best_config = None
        for i in valid_config:
            n = len(offline_jobs)
            if n == 0 :
                return 0.0000001
            
            all_combinations = list(permutations(i, n))
            
            for combo in all_combinations:
                config = []
               
                for z in combo:
                    config.append(config_map.get(z))
                throught =  self.Calculated_throughput(config, offline_jobs)
                
                if throught > best_obj:
                    best_config = config
                    best_obj = throught
                    
        config_list = []
        
        for i in jobs:
            if isinstance(i, online_job):
                config_list.append(config_map.get(online_config[online_jobs.index(i)]))
            if isinstance(i, offline_job):
                config_list.append(best_config[offline_jobs.index(i)])
        self.config_list[index] = config_list
      
        return best_obj
                


   
    def Calculated_throughput(self, config_list, jobs):
        throughput = 0
        global job_list
        
        for i in job_list:
            for j in range(0, len(jobs)):
             
                if jobs[j].model_name == i[0] and int(jobs[j].batch_Size) == int(i[1]) and config_list[j] == i[2]:
                    
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
    

    def state_change(self, GPU_index, job):
        index = self.GPU_list[GPU_index].index(job)
        self.GPU_list[GPU_index].remove(job)
        del self.config_list[GPU_index][index]
     
        self.throughput[GPU_index] =   self.miso_partition_optimizer(self.GPU_list[GPU_index], GPU_index)

        flag = True
        if not self.online_job_queue.empty():

            online_job = self.online_job_queue.get()
            result = self.miso_cluster(online_job)
            if result:
                flag = False
                
        
        if flag:
            if not self.offline_job_queue.empty():
                offline_job = self.offline_job_queue.get()
                result = self.miso_cluster(offline_job)
   
              