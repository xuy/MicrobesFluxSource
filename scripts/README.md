This folder will hold the watchdog daemon process that will run as a 
forever loop. 

We plan to use ansible for all interactions between this process (web01)
and the optimiation server (opt01). This script is running on web01.
Some scripts are running on opt01.

Watchdog runs a forever loop, and do the following in the loop:

   1. Query the task queue from web01, parse the list and figure out tasks that are pending.
   2. Get the uuid of TODO tasks, transmit/push the files into a delicated folder on opt01.
   3. Mark the task as "SCHEDULED".
   4. Invoke the script on opt01 to solve the optimization problem. Note that it is an async operation.
      This script does not wait until the optimization is done to continune.

         The script on server would do the following:
	   - Mark the task as "STARTED".
           - Solve the optimization problem using the file stored in the folder.
           - Mark the task as "SOLVED" or "NOT_SOLVED"

   5. Get the uuid of SOLVED tasks, transmit the results from opt01 to web01.
   6. Mark the task as ready to mail (this would trigger an email message to user).
   7. Get the uuid of NOT_SOLVED tasks, transmit the logs from opt01 to web01.
   8. Mark the task as FAILED, and mail the log to admin.

