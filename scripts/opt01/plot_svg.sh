#!/bin/bash
#$ -S /bin/bash
#$ -cwd

export PATH=/home/research/xuy:/cluster/cloud/bin:/home/research/xuy/local/bin:$PATH
echo "Going to mark current task ${TID}"

wget --spider "http://tanglab.engineering.wustl.edu/flux/task/mark/?tid=$TID"
# THE JOB has .adjlist suffix
echo "Going to call python to plot the current adjlist. Job name is ${JOB}"
if [ -e  /home/research/xuy/to_plot/${JOB}.adjlist ]
then echo "Found the adjlist file generated by MF, sending to python"
/home/research/xuy/local/bin/python /home/research/xuy/script/plot.py /home/research/xuy/to_plot/${JOB}.adjlist
fi
if [ -e /home/research/xuy/to_plot/${JOB}.adjlist_plot.svg ]
then echo "SVG generated."
cat /home/research/xuy/to_plot/${JOB}.adjlist_plot.svg | sed "s/stroke-width: 1.000000/stroke-width: 0.100000/g"  > /home/research/xuy/to_plot/${JOB}_plot.svg
rm /home/research/xuy/to_plot/${JOB}.adjlist_plot.svg
scp -i /home/research/xuy/xuy-seas /home/research/xuy/to_plot/${JOB}_plot.svg xuy@ssh.seas.wustl.edu:/project/research-www/tanglab/flux/temp/${JOB}_plot.svg
wget --spider "http://tanglab.engineering.wustl.edu/flux/task/mail/?tid=$TID"
fi