from file_transfer import transfer_file
from task_constants import *

files = ['solve_flux.sh', 'plot_network.sh' ]
for f in files:
    print "Copying file " + f + " to " + opt_server
    transfer_file(local_opt_path + f, opt_script_path + f)
