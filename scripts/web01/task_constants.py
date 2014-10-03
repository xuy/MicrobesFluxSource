# How often we run the watchdog loop.
watchdog_interval_sec = 5

# How often we process tasks in task queue.
task_delay_sec = 10
task_queue_list = 'http://www.microbesflux.org/flux/task/list/'
task_queue_mark = 'http://www.microbesflux.org/flux/task/mark/'
task_queue_mail = 'http://www.microbesflux.org/flux/task/mail/'


opt_server = 'cloud.seas.wustl.edu'
opt_username = 'tanglab-runner'
opt_keyfile = '/Users/exu/.ssh/tanglab-runner.rsa'

web_file_path = '/Users/exu/'
opt_file_path = '/home/research/tanglab-runner/task_queue/'
opt_script_path = '/home/research/tanglab-runner/script/'

try:
    from task_constants_local import *
except Exception:
    pass
