#!/usr/bin/python
from task_constants import *

from paramiko.client import SSHClient

client = SSHClient()
client.load_system_host_keys()
client.connect(hostname = opt_server,
               username = opt_username,
               key_filename = opt_keyfile)
output = client.exec_command('ls')
print output

from scp import SCPClient
scp = SCPClient(client.get_transport())
scp.put("ssh.py", "ssh.py")
scp.put("scp.py", "scp.py")
print client.exec_command('md5sum ssh.py scp.py')
client.close()

"""
  The UUID of a task will serve as the filename for all the files associated with the task.
  As well as the handle for marking/handling the task.

  A task has these states
    - TODO (we should verify that the file has been generated, if not, alert)
        copy the file on WEB01 to OPT01
        mark the task as GOING_TO_RUN
        submit the job as qsub (a shell script with param)
            (qsub should be able to mark something as READY_TO_MAIL

    - READY_TO_MAIL
        copy the file from OPT01 to WEB01
        send the email out
        mark the task as MAILED

    - MAILED:
        archive the log into a separate folder [optional]
        clean up the file on OPT01
        clean up the file on WEB01
        clean up/delete the task (not really delete, but just really done, with a flag)
"""

# Whether this is a web interface or a Django interface.
# It does not matter much, I can go by with web interface.

class Task:
    def __init__():
        self.task_type = 'dfa'
        self.uuid = '1234'
        self.state = 'TODO'
        self.suffix = ['.ampl']

# t is a Task
"""
def process_todo_task(t):
    copy_task(t.uuid, on_type)
"""

task_type_to_suffix = {
'fba': ('ampl', 'header', 'map'),
'dfba': ('ampl', 'header', 'map'),
'svg': ('adjlist',), }
