
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
            job_list = []
            while True:
                num = num + 1
                for i in range(0, len(miso.GPU_list)):
                    remove_jobs = []
                    for j in range(0, len(miso.GPU_list[i])):
                        if isinstance(miso.GPU_list[i][j], offline_job):
                           miso.GPU_list[i][j].progress = miso.GPU_list[i][j].progress + miso.GPU_list[i][j].speed
                           if miso.GPU_list[i][j].progress >= miso.GPU_list[i][j].epoch:
                               remove_jobs.append(miso.GPU_list[i][j])

                    if len(remove_jobs) != 0:
                        for z in remove_jobs:
                            z.end_time = num
                            job_list.append(z)
                            miso.state_change(i,z)


                        for j in range(0, len(miso.GPU_list[i])):
                            if isinstance(miso.GPU_list[i][j], online_job):
                                continue
                        
                            if isinstance(miso.GPU_list[i][j], offline_job):
                                if  miso.GPU_list[i][j].start_time == -1:
                                    miso.GPU_list[i][j].start_time = num
                                self.caculate_completion_time(miso.GPU_list[i][j], miso.config_list[i][j])
  
                if len(job_list) == 4:
                    for i in job_list:
                        print(i)
                    break
            self.caculate_system_metrics(jobs=job_list)
            

    def caculate_completion_time(self, offline_job, config):
        global job_list
        for i in job_list:
            if i.model_name == offline_job.model_name and str(i.batch_Size) == str(offline_job.batch_Size) and config == i.config:
                offline_job.speed = 1000/float(i.average_time)
                break

    def caculate_system_metrics(self, jobs):
        avarage_queue_time = 0
        JCT = 0
        makespan = 0
        num = len(jobs)
        for i in jobs:
            avarage_queue_time = avarage_queue_time + int(i.start_time) - int(i.submit_time)
            JCT = JCT + int(i.end_time) - int(i.submit_time)
            if int(i.end_time) > makespan:
                makespan = i.end_time
        

        avarage_queue_time = avarage_queue_time/num
        JCT = JCT/num

        print("avarage_queue_time : ", avarage_queue_time)
        print("JCT: ", JCT)
        print("makespan: ", makespan)





test1  = online_job('resnet152', '16' , 80)
online_jobs = []
online_jobs.append(test1)


offline_jobs = []

test2  = offline_job('resnet152', '32' , 100000)
test3  = offline_job('resnet50', '32' , 100000)
test4  = offline_job('bert', '32' , 100000)
test5  = offline_job('vgg16', '32' , 100000)
offline_jobs.append(test2)
offline_jobs.append(test3)
offline_jobs.append(test4)
offline_jobs.append(test5)

test = simulator(GPU_num=1, algorithm='miso', online_jobs= online_jobs, offline_jobs=offline_jobs)