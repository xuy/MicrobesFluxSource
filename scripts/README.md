This folder contains scripts that handles optimization and plotting tasks.

When user makes a FBA/dFBA request, or a SVG request, we generate a task and a set of
temporary files that are necessary for that task. The Django framework, running on the
web server (web01), would maintain the task queue, as well as the set of intermediate
files.

Web01 is not powerful enough for solving optimization problem though. Thus, we would need
to employ another machine, opt01, for optimization.

We run a script (watchdog.py) on web01 to process the task queue. The script does three
things:

1. copy files associated with 'TODO' tasks to opt01.
2. invoke a script on opt01 to do optimization or plotting
3. gather results from opt01 and copy those back to web01.

A caveat here is Step 2 is executed on Sun Grid Engine. Scripts (solve_fba.sh etc.)
under opt01 are submitted through qsub instead of getting executed directly. Thus,
we communicate with task queue in those scripts once Step 2 is done.




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

