
import sys
sys.path.append('/home/zbw/MIG/MIG_Schedule')
from schedule.scheduler.miso_scheduler import online_job, offline_job, miso_sheduler


from schedule.scheduler.muxflow_scheduler import muxflow_sheduler
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
            miso = miso_sheduler()
            GPU_list = []
            for i in range(0, self.GPU_num):
                GPU_list.append([])

            for i in self.online_jobs:
               
               miso.miso_cluster(i)

            for j in self.offline_jobs:
                if miso_sheduler
                miso.miso_cluster(j)

    def cacculate_completion_time(self, offline_job, config):
        pass