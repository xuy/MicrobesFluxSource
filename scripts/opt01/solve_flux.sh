#!/bin/bash
#$ -S /bin/bash
#$ -cwd
HOME=/home/research/tanglab-runner/
TASK_QUEUE='http://www.microbesflux.org/flux/task/mark/?tid='
TASK_FOLDER=task_queue/
TASK_STATUS_START='&status=OPT_START'
TASK_STATUS_END='&status=OPT_END'
TASK_STATUS_FAIL='&status=OPT_FAIL'

# PATH is used to locate ampl_lic, ampl and ipopt
export PATH=${HOME}:/cluster/cloud/bin/:/cluster/cloud/Ipopt-3.8.3/bin:$PATH
echo "Going to mark current task "
wget --spider ${TASK_QUEUE}${TID}${TASK_STATUS_START}
echo `date "+%Y%m%d%H%M$S"` ampl $USER >> /cluster/cloud/var/log/app-usage  # AMPL usage, requested by seas.
ampl ${HOME}${TASK_FOLDER}${UUID}.ampl > ${HOME}${TASK_FOLDER}${UUID}.result
if [ $? -eq 0 ]
then
    wget --spider ${TASK_QUEUE}${TID}${TASK_STATUS_END}
else
    wget --spider ${TASK_QUEUE}${TID}${TASK_STATUS_FAIL}
fi
