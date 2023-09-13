
import sys
import re
import glob
sys.path.append('/home/zbw/MIG/MIG_Schedule')
from schedule.scheduler.miso_scheduler import online_job, offline_job, miso_sheduler
from schedule.scheduler.scheduler import I_sheduler
from schedule.scheduler.muxflow_scheduler import muxflow_sheduler
from jobs.profile.standardized_throughput import get_job_list


job_list = get_job_list()
dir = '/home/zbw/MIG/MIG_Schedule/jobs/profile/result/'
throught_list = {}
file_list = glob.glob(dir + '2_*.txt')
for file_name in file_list:
    with open(file_name, 'r') as f:
        file_name = file_name.replace("/home/zbw/MIG/MIG_Schedule/jobs/profile/result/", "")
       
        pattern = r'2_(?!.*_online\.txt)(.*?)\.txt'
        match = re.match(pattern, file_name)
        extracted_text = ''
        if match:
            extracted_text = match.group(1)
        else:
            f.close()
            continue
    
        throught_list[extracted_text] = []
        num = 0
        for line in f:
            throught_list[extracted_text].append([])
            line = line.strip()
            throught_list[extracted_text][num].append(line.split(" ")[0])
            throught_list[extracted_text][num].append(line.split(" ")[1])
            throught_list[extracted_text][num].append(line.split(" ")[2])
            throught_list[extracted_text][num].append(line.split(" ")[3])
            throught_list[extracted_text][num].append(line.split(" ")[4])
            throught_list[extracted_text][num].append(line.split(" ")[5])
            num = num + 1
    f.close()



class simulator:
    def __init__(self, GPU_num, algorithm, online_jobs, offline_jobs, num=4):
        self.GPU_num = GPU_num
        self.algorithm = algorithm
        self.online_jobs = online_jobs
        self.offline_jobs = offline_jobs
        self.num = num
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
              
                if len(job_list) == self.num:
                    for i in job_list:
                        print(i)
                    break
            self.caculate_system_metrics(jobs=job_list)

        if self.algorithm == 'me':
            GPU_list = []
            for i in range(0, self.GPU_num):
                GPU_list.append([])
            
            scheduler = I_sheduler(GPU_list= GPU_list)
            for i in self.online_jobs:
                scheduler.I_cluster(i)

            for j in self.offline_jobs:
                if scheduler.I_cluster(j):
                    j.start_time = 0 
            
            for i in range(0, len(scheduler.GPU_list)):
                configs = scheduler.config_list[i]

                for j in range(0, len(scheduler.GPU_list[i])):
                    if len(scheduler.GPU_list[i][j]) == 1:
                        if isinstance(scheduler.GPU_list[i][j][0], online_job):
                            continue
                        if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                            self.caculate_completion_time(scheduler.GPU_list[i][j][0], configs[j])
                    
                    else:
                        if isinstance(scheduler.GPU_list[i][j][0], online_job):
                            self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][1], scheduler.GPU_list[i][j][0] ,configs[j])
                        else:
                            self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][0], scheduler.GPU_list[i][j][1] ,configs[j])
            

            num = 0
            job_list = []
            while True:
                num = num + 1
                for i in range(0, len(scheduler.GPU_list)):
                 
                    remove_jobs = []
                    for j in range(0, len(scheduler.GPU_list[i])):
                        if len(scheduler.GPU_list[i][j]) == 1:
                            if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                scheduler.GPU_list[i][j][0].progress = scheduler.GPU_list[i][j][0].progress + scheduler.GPU_list[i][j][0].speed
                                if scheduler.GPU_list[i][j][0].progress >= scheduler.GPU_list[i][j][0].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][0])
                        else:
                            if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                scheduler.GPU_list[i][j][0].progress = scheduler.GPU_list[i][j][0].progress + scheduler.GPU_list[i][j][0].speed
                                if scheduler.GPU_list[i][j][0].progress >= scheduler.GPU_list[i][j][0].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][0])
                            else:
                                scheduler.GPU_list[i][j][1].progress = scheduler.GPU_list[i][j][1].progress + scheduler.GPU_list[i][j][1].speed
                                if scheduler.GPU_list[i][j][1].progress >= scheduler.GPU_list[i][j][1].epoch:
                                    remove_jobs.append(scheduler.GPU_list[i][j][1])

                    if len(remove_jobs) != 0:
                        for z in remove_jobs:
                            z.end_time = num
                            job_list.append(z)
                         
                            scheduler.state_change(i,z)
                     

                        
                        for j in range(0, len(scheduler.GPU_list[i])):
                            if len(scheduler.GPU_list[i][j]) == 1:
                                if isinstance(scheduler.GPU_list[i][j][0], online_job):
                                    continue
                                if isinstance(scheduler.GPU_list[i][j][0], offline_job):
                                    if  scheduler.GPU_list[i][j][0].start_time == -1:
                                        scheduler.GPU_list[i][j][0].start_time = num
                    
                                    self.caculate_completion_time(scheduler.GPU_list[i][j][0], scheduler.config_list[i][j])
                    
                            else:
                                if isinstance(scheduler.GPU_list[i][j][0], online_job):
                                    if  scheduler.GPU_list[i][j][1].start_time == -1:
                                        scheduler.GPU_list[i][j][1].start_time = num
                                    self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][1], scheduler.GPU_list[i][j][0], scheduler.config_list[i][j])
                                else:
                                    if  scheduler.GPU_list[i][j][0].start_time == -1:
                                        scheduler.GPU_list[i][j][0].start_time = num
                                    self.caculate_completion_time_concurrency(scheduler.GPU_list[i][j][0], scheduler.GPU_list[i][j][1], scheduler.config_list[i][j])

               
                if len(job_list) == self.num:
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
    
    def caculate_completion_time_concurrency(self, offline_job:offline_job, online_job:online_job, config):
        for i in throught_list[config]:

            if i[0] == online_job.model_name and int(i[1]) == int(online_job.batch_Size) and i[3] == offline_job.model_name and \
                int(i[4]) == int(offline_job.batch_Size):
                offline_job.speed = 1000/float(i[5])
                
            if i[0] == offline_job.model_name and int(i[1]) == int(offline_job.batch_Size) and i[3] == online_job.model_name and \
                int(i[4]) == int(online_job.batch_Size):
                offline_job.speed =  1000/float(i[2])

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









offline_jobs = []
online_jobs = []


# online_jobs.append(online_job('resnet152', '16' , 50))
online_jobs.append(online_job('resnet50', '32' , 49))
online_jobs.append(online_job('bert', '8' , 90))
# online_jobs.append(online_job('resnet50', '32' , 49))

# online_jobs.append(online_job('resnet152', '16' , 80))
# online_jobs.append(online_job('resnet50', '16' , 80))
# online_jobs.append(online_job('bert', '8' , 80))
# online_jobs.append(online_job('resnet50', '16' , 80))

offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000)) 

offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))


offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))
test = simulator(GPU_num=2, algorithm='me', online_jobs= online_jobs, offline_jobs=offline_jobs, num=len(offline_jobs))



offline_jobs = []
online_jobs = []

# online_jobs.append(online_job('resnet152', '16' , 80))
# online_jobs.append(online_job('resnet50', '16' , 80))
# online_jobs.append(online_job('bert', '8' , 80))
# online_jobs.append(online_job('resnet50', '16' , 80))
# online_jobs.append(online_job('resnet152', '16' , 50))
online_jobs.append(online_job('resnet50', '32' , 49))
online_jobs.append(online_job('bert', '8' , 90))
# online_jobs.append(online_job('resnet50', '32' , 49))

offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000)) 

offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))


offline_jobs.append(offline_job('resnet152', '32' , 100000))
offline_jobs.append(offline_job('resnet50', '32' , 100000))
offline_jobs.append(offline_job('vgg16', '32' , 100000))
offline_jobs.append(offline_job('bert', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))

offline_jobs.append(offline_job('vgg16', '8' , 100000))
offline_jobs.append(offline_job('vgg19', '16' , 100000))
offline_jobs.append(offline_job('resnet50', '8' , 100000))
offline_jobs.append(offline_job('resnet101', '32' , 100000))
test2 = simulator(GPU_num=2, algorithm='miso', online_jobs= online_jobs, offline_jobs=offline_jobs, num=len(offline_jobs))
# offline_jobs = []
# online_jobs = []
# online_jobs.append(online_job('resnet152', '16' , 80))
# offline_jobs.append(offline_job('resnet152', '32' , 100000))
# offline_jobs.append(offline_job('resnet50', '32' , 100000))
# offline_jobs.append(offline_job('vgg16', '32' , 100000))
# offline_jobs.append(offline_job('bert', '32' , 100000))
