
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')
from schedule.scheduler.miso_scheduler import online_job, offline_job, miso_sheduler
from schedule.scheduler.muxflow_scheduler import muxflow_sheduler
from jobs.profile.standardized_throughput import get_job_list


job_list = get_job_list()



class simulator:
    def __init__(self, GPU_num, algorithm, online_jobs, offline_jobs):
        self.GPU_num = GPU_num
        self.algorithm = algorithm
        self.online_jobs = online_jobs
        self.offline_jobs = offline_jobs

        self.queue_time = []
        self.JCT = []
        self.config_num = 0
        self.simulate()

    def simulate(self):
        if self.algorithm == 'miso':
            checkpoint_time = 0
            GPU_list = []
            for i in range(0, self.GPU_num):
                GPU_list.append([])


            miso = miso_sheduler(GPU_list= GPU_list)
            for i in self.online_jobs:
               miso.miso_cluster(i)

            for j in self.offline_jobs:
                if  miso.miso_cluster(j):
                    j.start_time = 0 

            for i in range(0, len(miso.GPU_list)):
                jobs = miso.GPU_list[i]
                configs = miso.config_list[i]


                for j in range(0, len(jobs)):
                    if isinstance(jobs[j], online_job):
                        continue
                        
                    if isinstance(jobs[j], offline_job):
                        self.caculate_completion_time(jobs[j], configs[j])
            

            num = 0
            while True:
                num = num + 1
                for i in range(0, len(miso.GPU_list)):
                    for j in miso.GPU_list[i]:
                        if isinstance

            

    def caculate_completion_time(self, offline_job, config):
        global job_list
        for i in job_list:
            if i.model_name == offline_job.model_name and str(i.batch_Size) == str(offline_job.batch_Size) and config == i.config:
                offline_job.time = int(offline_job.epoch) * float(i.average_time)/1000
                break


test1  = online_job('resnet152', '16' , 80)
online_jobs = []
online_jobs.append(test1)


offline_jobs = []

test2  = offline_job('resnet152', '8' , 800)
test3  = offline_job('resnet50', '16' , 800)

offline_jobs.append(test2)
offline_jobs.append(test3)


test = simulator(GPU_num=1, algorithm='miso', online_jobs= online_jobs, offline_jobs=offline_jobs)