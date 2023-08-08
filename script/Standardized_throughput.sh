#!/bin/bash

# online job profile
CU_DEV=CUDA_VISIBLE_DEVICES
dev0='GPU-08dffabe-6be4-81d7-ba7d-1d96612fb099'
GPU_ID=0
workdir=/home/zbw/MIG/MIG_Schedule
batch_size=("32" "16" "8" "4")
model_list=("resnet50" "resnet101" "resnet152" "vgg19" "vgg16" "inception_v3" "unet" "deeplabv3" "mobilenet_v2" "open_unmix" "alexnet" "bert")



GPU_list=$workdir/MIG_partitions.txt
InstanceID_list=$workdir/ID.txt
get_uuid_pick="python $workdir/util/getUuidInfo.py --input ${GPU_list} --raw 0 --pick 1 --ch"
get_uuid_unpick="python $workdir/util/getUuidInfo.py --input ${GPU_list} --raw 0 --pick 0 --ch"
get_IID="python $workdir/util/readID.py --input ${InstanceID_list}"

# source /home/hpcroot/anaconda3/etc/profile.d/conda.sh


function create {
    sudo nvidia-smi mig -cgi $1 -C > ${InstanceID_list}
    nvidia-smi -L >${GPU_list}
    python $workdir/util/getUuidAll.py --input $GPU_list --raw 1
    echo "Successfully created"
    ID=$(${get_IID})
}

function destroy {
    sudo nvidia-smi mig -dci -i 0 -gi $1 -ci 0
    sudo nvidia-smi mig -dgi -i 0 -gi $1
}

function test {
    prof_id=$1
    info=$2
   
    echo "Testing on mig: " $info
    create $prof_id
    uuid=$(${get_uuid_pick} ${info})
    echo $uuid
    for model in ${model_list[@]}; do
        for batch in ${batch_size[@]}; do
            python $workdir/main.py --config  $info --task $model --batch $batch
        done
    done
    sleep 3
    destroy $ID
}

sudo nvidia-smi -i 0 -mig 0
for model in ${model_list[@]}; do
    for batch in ${batch_size[@]}; do
        python $workdir/main.py --config  baseline --task $model --batch $batch
    done
done
echo 'open MIG model'
sudo nvidia-smi -i 0 -mig 1

test 0 1c-7g-80gb 
test 5 1c-4g-40gb 
test 9 1c-3g-40gb 
test 14 1c-2g-20gb
test 19 1c-1g-10gb

echo 'close MIG model'
sleep 5
sudo nvidia-smi -i 0 -mig 0