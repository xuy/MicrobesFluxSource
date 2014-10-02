#!/bin/bash
#$ -S /bin/bash
#$ -cwd
HOME=/home/research/tanglab-runner
TASK_QUEUE='http://tanglab.engineering.wustl.edu/flux/task/mark/?tid='

# PATH is used to locate ampl_lic, ampl and ipopt
export PATH=${HOME}:/cluster/cloud/bin/:/cluster/cloud/Ipopt-3.8.3/bin:$PATH
echo "Going to mark current task "
wget --spider ${TASK_QUEUE}${TID}
ampl ${HOME}/ampl_to_run/${JOB}.ampl > /home/research/xuy/ampl_to_run/${JOB}.result
# TODO(xuy): task mark should have better support.
# wget --spider "http://tanglab.engineering.wustl.edu/flux/task/mail/?tid=$TID"
