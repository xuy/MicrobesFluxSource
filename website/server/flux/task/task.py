from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.http import HttpResponse
from flux.models import Task

########### Helper functions ###########
import sys

from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from django.http import HttpResponse

COMMASPACE = ', '
def send_mail(address, attachment, title = ""):
    subject = 'Mail from MicrobesFlux --' + title
    fromaddr = "tanglab@seas.wustl.edu"
    toaddrs = [address, ]
    content = "Dear MicrobesFlux User, thank you for using our website. -- MicrobesFlux"
    email = EmailMessage(subject, content, fromaddr, toaddrs)

    # Attachments.
    fs = FileSystemStorage()
    # Attachment is a pair: (uuid file name, user file name)
    fp = fs.open(attachment[0], "rb")
    email.attach(attachment[1], fp.read(), 'text/plain')
    fp.close()
    email.send(fail_silently=False)

def generate_report(file_uuid):
    fs = FileSystemStorage()

    report_header = file_uuid + '.header'
    ampl_file     = file_uuid + '.ampl'
    variable_map  = file_uuid + '.map'
    ampl_result   = file_uuid + '.result'
    # report = concat(header, ampl, map, result)
    report_file   = file_uuid + '.report'

    # Step 0. Write the report file
    finaloutput = fs.open(report_file, "w")

    #### Step 0.1 Read the variable correspondence
    fmap  = fs.open(variable_map, "r")
    d = {}
    for l in fmap:
        vname, oldname = l.split()[:2]
        d[vname]  = oldname
    fmap.close()

    ### Step 1: transfer .header to _report.txt
    fheader = fs.open(report_header, "r")
    for l in fheader:
        finaloutput.write(l)
    fheader.close()

    ### Step 2: transfer ampl to report
    fampl = fs.open(ampl_file, "r")
    for l in fampl:
        finaloutput.write(l)
    fampl.close()

    ### Step 3: conversions
    finaloutput.write("\n\n ===  Name conversions between variables and fluxes === \n")
    fmap = fs.open(variable_map, "r")
    for l in fmap:
        finaloutput.write(l)
    fmap.close()

    finaloutput.write("\n\n======== Results ========= \n")

    fampl_result = fs.open(ampl_result, "r")
    fl = fampl_result.xreadlines()
    for l in fl:
        temp = l.split()
        if len(temp) == 2 and l[0]=="V":
            name, value = l.split()
            finaloutput.write(d[name])
            finaloutput.write( "\t -> \t ")
            finaloutput.write( value)
            finaloutput.write( "\n" )
        else:
            finaloutput.write(l)
    fampl_result.close()
    finaloutput.close()

########## Methods for external use ####
def task_list(request):
    all_task = Task.objects.all()
    total = len(all_task)
    if total > 50:
        all_task = all_task[total-50:]  # take last 50
    l = []
    for t in all_task:
        l.append(str(t))
    return HttpResponse(content = '\n'.join(l), status = 200, content_type = "text/html")

def task_remove(request):
    tid = request.GET['tid']
    try:
        to_remove = Task.objects.get(task_id = tid)
        to_remove.delete()
        return HttpResponse(content = "Task Removed", status = 200, content_type = "text/html")
    except Task.DoesNotExist:
        return HttpResponse(content = "No such task", status = 200, content_type = "text/html")

def cleanup_files(files):
    fs = FileSystemStorage()
    removed = []
    for f in files:
        if fs.exists(f):
            fs.delete(f)
            removed.append(f)
    return removed

def task_cleanup(request):
    tid = request.GET['tid']
    try:
        to_remove = Task.objects.get(task_id = tid)
        uuid = to_remove.uuid
        task_type = to_remove.task_type
        if task_type == 'fba' or task_type == 'dfba':
            files = [ uuid + suffix for suffix in ['.ampl', '.map', '.result', '.header', '.report']]
            removed_files = cleanup_files(files)
        else:
            files = [ uuid + suffix for suffix in ['.svg', '.adjlist']]
            removed_files = cleanup_files(files)
        to_remove.delete()
        return HttpResponse(content = "Cleaned up files: " + ','.join(removed_files), status = 200, content_type = "text/html")
    except Task.DoesNotExist:
        return HttpResponse(content = "No such task", status = 200, content_type = "text/html")

def task_add(request):
    t_type = request.GET['type']
    t_file = request.GET['task']
    t_email = request.GET['email']
    t_addif = ""
    if request.GET.has_key('file'):
        t_addif = request.GET['file']
    t = Task(task_type = t_type, main_file = t_file, email = t_email, additional_file = t_addif, status = "TODO")
    t.save()
    return HttpResponse(content = """ Task added  """, status = 200, content_type = "text/html")

def task_unmark(request):
    tid = request.GET['tid']
    try:
        to_mark = Task.objects.get(task_id = tid)
        to_mark.status = "TODO"
        to_mark.save()
        return HttpResponse(content = "Task Un-marked", status = 200, content_type = "text/html")
    except Task.DoesNotExist:
        return HttpResponse(content = "No such task", status = 200, content_type = "text/html")

def task_mark(request):
    tid = request.GET['tid']
    status = 'CLOUD'
    if request.GET.has_key('status'):
        status = request.GET['status']
    try:
        to_mark = Task.objects.get(task_id = tid)
        to_mark.status = status
        # TODO: send out a piece of email, saying it is enqueued
        to_mark.save()
        return HttpResponse(content = "Task Marked", status = 200, content_type = "text/html")
    except Task.DoesNotExist:
        return HttpResponse(content = "No such task", status = 200, content_type = "text/html")

def task_mail(request):
    tid = request.GET['tid']
    try:
        task = Task.objects.get(task_id = tid)
        model_name = task.main_file.split(".")[0]  # take the base name
        address = task.email
        uuid = str(task.uuid)
        if task.task_type == "fba":
            generate_report(uuid)
            send_mail(address, (uuid + '.report', model_name + "_fba_report.txt"), title = "FBA")
        elif task.task_type == "dfba":
            generate_report(uuid)
            send_mail(address, (uuid + '.report', model_name + "_dfba_report.txt"), title = "dFBA")
        else:
            send_mail(address, (uuid + '.svg', model_name +'.svg'), title = ' SVG ' + model_name)
        task.status = 'MAIL_SENT'
        task.save()
        return HttpResponse(content = """ Mail sent """, status = 200, content_type = "text/html")
    except Task.DoesNotExist:
        return HttpResponse(content = "No such task", status = 200, content_type = "text/html")

from django.shortcuts import render
from django.shortcuts import get_list_or_404

def task_prettylist(request):
    all_task = Task.objects.all()
    total = len(all_task)
    if total > 50:
        all_task = all_task[total-50:]  # take last 50
    task_objects = []
    for t in all_task:
        task_objects.append(t)
    return render(request, 'table.html', {'tasks':task_objects})
