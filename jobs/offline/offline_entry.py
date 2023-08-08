from MLP_train import MLP_train
from resnet_train import resnet_train
from vgg_train import vgg_train
from alexnet_train import alxnet_train
import subprocess
import argparse
task_table = {
    'mlp' : MLP_train,
    'resnet':  resnet_train,
    'vgg19': vgg_train,
    'alexnet': alxnet_train,
}
def run_command(command):
    try:
        # 使用subprocess.run来执行命令
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,  # 捕获标准输出流
            stderr=subprocess.PIPE,  # 捕获标准错误流
            text=True,  # 以文本形式获取输出
            shell=True  # 允许在shell中运行命令（如果需要）
        )
        
        print("标准输出：")
        print(result.stdout)
        if result.stderr:
            print("标准错误：")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print("命令执行出错:", e)


parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str)
args = parser.parse_args()

task = args.model
print(task)
if task == 'unet':
    command_to_run = "cd /home/zbw/MIG/MIG_Schedule/jobs/offline/Unet && conda run -n Abacus python train.py --amp"
    run_command(command_to_run)
else:
    entry = task_table[task]
    entry()


