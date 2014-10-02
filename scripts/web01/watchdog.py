#!/usr/bin/python
from task_constants import *
from task_util import parse_task
from file_transfer import transfer_file
from file_transfer import run_command

import os.path
import requests
import urllib2
import time

def mark_task(tid, status):
    print "going to mark task " + tid + ' as ' + status
    payload = {'tid': tid, 'status': status}
    try:
        r = requests.get(task_queue_mark, params = payload)
        print r.url
        print r.text
    except requests.exceptions.RequestException, e:
        print "Cannot mark task " + tid + ' to status ' + status
        print e

def copy_to_server(task):
    task_type = task['type']
    tid = task['id']
    uuid = task['uuid']
    print "Going to copy task uuid " + uuid  + " to server"
    if task_type == "fba" or task_type == 'dfba':
        filename = uuid + '.ampl'
    else:   # svg
        filename = uuid + '.adjlist'
    if os.path.isfile(web_file_path  + filename):
        transfer_file(filename)
        return True
    else:
        mark_task(tid, 'FILE_MISS')
        return False

def get_job_name(task_type):
    """ Maps task type to the script name that will be submitted via qsub"""
    if task_type == 'fba':
        return 'solve_fba.sh'
    elif task_type == 'dfba':
        return 'solve_dfba.sh'
    else:
        return 'plot_svg.sh'

def parse_task_submission_output(stdout, stderr):
    if len(stdout) > 1 or len(stdout) < 1:
        print "unexpected output format ", stdout
        return 
    jobline = stdout[0]
    if not jobline.startswith('Your job'):
        print 'unexpected output for submitting jobs ' + jobline
    qsub_info = jobline.split()
    qsub_id = qsub_info[2]
    qsub_job = qsub_info[3].strip('()"')
    print qsub_id, qsub_job

def submit_task(task):
    task_type = task['type']
    qsub_command = ['qsub',
                    '-v UUID=' + task['uuid'],
                    '-v TID=' + task['id'],
                    get_job_name(task_type)]
    command = []
    command.append('cd ' + opt_script_path)
    command.append(' '.join(qsub_command))
    return run_command(';'.join(command))

def handle_todo_task(task):
    task_type = task['type']
    uuid = task['uuid']
    tid = task['id']
    if not copy_to_server(task):
        return 
    mark_task(tid, 'OPT_INIT')
    stdout, stderr = submit_task(task)
    print stdout, stderr
    parse_task_submission_output(stdout, stderr)

def run_forever():
    while True:
        print "Reading task queue ... "
        try:
            r = requests.get(task_queue_list)
        except requests.exceptions.RequestException, e:
            # It should not crash the whole watchdog.
            print e
            continue
        list = []
        for l in r:
            list.append(l)
        if not list:
            continue
        for l in list:
            print "from list ", l
            task = parse_task(l)
            print task
            problem= task['name']
            type = task['type']
            status = task['status']
            if status == 'TODO':
                handle_todo_task(task)
                time.sleep(task_delay_sec)
        time.sleep(watchdog_interval_sec)

if __name__ == '__main__':
    run_forever()
