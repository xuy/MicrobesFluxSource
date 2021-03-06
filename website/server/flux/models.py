from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from constants import user_filebase

""" This Profile model describes a user's optimization problem
and pathway target.
"""

class Profile(models.Model):
    name = models.CharField(max_length = 30)
    user = models.ForeignKey(User)
    diskfile    = models.FileField(max_length=100, upload_to=user_filebase + "fba")
    status      = models.CharField(max_length= 30)
    model_type  = models.CharField(max_length= 10)
    submitted   = models.BooleanField(default=False)


class Compound(models.Model):
    name      = models.CharField(max_length = 10)
    alias     = models.CharField(max_length = 10)
    long_name = models.CharField(max_length =140)

    def __unicode__(self):
        return self.name + " A:" + self.alias + " L:" + self.long_name

class Task(models.Model):
    task_id   =  models.AutoField(primary_key = True)
    task_type =  models.CharField(max_length = 10)
    # The following two fields are deprecated in favor of using uuid.
    main_file =  models.CharField(max_length = 50)
    additional_file =  models.CharField(max_length = 50)
    email     = models.EmailField(max_length = 75)
    status    = models.CharField(max_length = 10)
    # Django stable release does not support UUIDField (yet).
    uuid =  models.CharField(max_length=250, unique=True, null=False, blank=False, default=uuid4, editable = False)
    submitted_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        information = [str(self.task_id), self.main_file, self.task_type, self.email, self.status, self.uuid, str(self.submitted_date)]
        return ','.join(information)

# User can save/load their models. We put the serialized PathwayNetwork
# object in "Collection".
class Collection(models.Model):
    id =  models.AutoField(primary_key = True)
    user = models.ForeignKey(User)
    name = models.CharField(max_length = 140)
    pickle = models.BinaryField()

# Intermediate file storage
class UserFile(models.Model):
    file_id = models.AutoField(primary_key = True)
    user_id = models.ForeignKey(User)
    collection_id = models.ForeignKey(Collection)
