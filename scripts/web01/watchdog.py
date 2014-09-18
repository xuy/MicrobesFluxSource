#!/usr/bin/python

### TODO(xuy): change this to anisble script.
import time
from urllib import urlopen
import subprocess

while True:
	time.sleep(5)
	print "Check List"
	f = urlopen("http://tanglab.engineering.wustl.edu/flux/task/list/")
	list = []
	for l in f:
		list.append(l)
	if not list:
		continue
	#l = list[0]
	#if not l or l[0]!='2':
	#	continue
	for l in list:
		print "Will parse log",
		print l
		ls = l.split(',')
		tid, pro, type, email = ls[:4]
		if len(ls) < 5:
			continue
		status = ls[4]
		additional_file = ls[5]
		print "additional file", additional_file
		problem= pro
		print "status is ", status
		if status != "TODO":
			continue
		print "Going to handle task ", problem, " type ", type
		if type == "$TYPE":
			continue
		elif type == "fba":
			p = subprocess.Popen("scp -i /home/research/xuy/xuy-seas xuy@ssh.seas.wustl.edu:/project/research-www/tanglab/flux/temp/"+problem + ".ampl  /home/research/xuy/ampl_to_run/", shell = True)
			p = subprocess.Popen('wget --spider \"http://tanglab.engineering.wustl.edu/flux/task/mark/?tid='+tid+'"', shell = True)
			p = subprocess.Popen("cd /home/research/xuy/script; qsub -v JOB=" + problem + " -v TID="+tid +" fbajob.sh", shell = True)
		elif type == "svg":
			print "watchdog is going to scp " + problem + " to to_plot"
			p = subprocess.Popen("scp -i /home/research/xuy/xuy-seas xuy@ssh.seas.wustl.edu:/project/research-www/tanglab/flux/temp/"+problem + ".adjlist /home/research/xuy/to_plot/", shell = True)
			p = subprocess.Popen('wget --spider \"http://tanglab.engineering.wustl.edu/flux/task/mark/?tid='+tid+'"', shell = True)
			p = subprocess.Popen("cd /home/research/xuy/script; qsub -v JOB=" + problem + " -v TID="+tid +" plotjob.sh", shell = True)
		elif type == "dfba":
			# print "Going to solve a dfba task", l
			p = subprocess.Popen("scp -i /home/research/xuy/xuy-seas xuy@ssh.seas.wustl.edu:/project/research-www/tanglab/flux/temp/"+problem + ".ampl  /home/research/xuy/ampl_to_run/"+problem+"_dfba.ampl", shell = True)
			p = subprocess.Popen('wget --spider \"http://tanglab.engineering.wustl.edu/flux/task/mark/?tid='+tid+'"', shell = True)
			# and then give it as JOB to the qsub
			p = subprocess.Popen("cd /home/research/xuy/script; qsub -v JOB=" + problem  + " -v TID="+tid +" dfbajob.sh", shell = True)
		time.sleep(10)
		break
