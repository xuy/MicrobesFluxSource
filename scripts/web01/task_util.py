from task_constants import *

def parse_task(l):
    ls = l.split(',')
    task = {}
    task['id']          = ls[0]
    task['name']        = ls[1]
    task['type']        = ls[2]
    task['email']       = ls[3]
    task['status']      = ls[4]
    task['uuid']        = ls[5]
    task['date']        = ls[6]
    if task['type'] not in ['fba', 'dfba', 'svg']:
        raise Exception('no such task type')
    return task


