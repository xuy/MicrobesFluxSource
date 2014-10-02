#!/usr/bin/python
from task_constants import *
from task_util import parse_task
from file_transfer import transfer_file

from urllib import urlopen

import time
import subprocess
import urllib2

def copy_to_server(task_type, uuid):
    print "Going to copy task uuid " + uuid  + " to server"
    if task_type == "fba" or task_type == 'dfba':
        filename = uuid + '.ampl'
    else:   # svg
        filename = uuid + '.adjlist'
    transfer_file(filename)

def get_job_name(task_type):
    """ Maps task type to the script name that will be submitted via qsub"""
    if task_type == 'fba':
        return 'solve_fba.sh'
    elif task_type == 'dfba':
        return 'solve_dfba.sh'
    else:
        return 'plot_svg.sh'

def mark_task(uuid):
    print "going to mark task " + uuid + ' as enqueue'

def submit_task(task):
    task_type = task['type']
    qsub_command = ['qsub',
                    '-v UUID=' + task['uuid'],
                    '-v TID=' + task['id'],
                    get_job_name(task_type)]
    command = []
    command.append('cd ' + opt_script_path)
    command.append(' '.join(qsub_command))
    print ';'.join(command)

def handle_todo_task(task):
    type = task['type']
    uuid = task['uuid']
    id = task['id']
    copy_to_server(type, uuid)
    mark_task(uuid)
    submit_task(task)

def run_forever():
    while True:
        print "Reading task queue ... "
        try:
            f = urlopen(task_queue)
        except urllib2.URLError, e:
            # It should not crash the whole watchdog.
            print e
            continue
        list = []
        for l in f:
            list.append(l)
        if not list:
            continue
        for l in list:
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
