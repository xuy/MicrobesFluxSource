from paramiko.client import SSHClient
from scp import SCPClient
from task_constants import *

def transfer_file(source, target, direction = 'put'):
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname = opt_server,
                   username = opt_username,
                   key_filename = opt_keyfile)
    scp = SCPClient(client.get_transport())
    if direction == 'put':
        scp.put(source, target)
    else:
        scp.get(source, target)
    client.close()

def run_command(command):
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname = opt_server,
                   username = opt_username,
                   key_filename = opt_keyfile)
    (stdin, stdout, stderr) = client.exec_command(command)
    return (stdout.readlines(), stderr.readlines())
