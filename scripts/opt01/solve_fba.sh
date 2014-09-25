#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#echo $JOB
#echo $TID
export PATH=/home/research/xuy:/cluster/cloud/bin:/home/research/xuy/local/bin:/cluster/cloud/Ipopt-3.8.3/bin:$PATH
#echo $PATH
echo "Going to mark current task "
wget --spider "http://tanglab.engineering.wustl.edu/flux/task/mark/?tid=$TID"
ampl /home/research/xuy/ampl_to_run/${JOB}.ampl > /home/research/xuy/ampl_to_run/$JOB.result
# TODO(xuy): remove this copy and mark
scp -i /home/research/xuy/xuy-seas /home/research/xuy/ampl_to_run/${JOB}.result xuy@ssh.seas.wustl.edu:/project/research-www/tanglab/flux/temp/${JOB}_fba_result.txt
wget --spider "http://tanglab.engineering.wustl.edu/flux/task/mail/?tid=$TID"
# This is used by qsub
