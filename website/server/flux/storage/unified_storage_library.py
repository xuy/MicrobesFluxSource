#!/usr/bin/python

""" This is the
    unified storage library

it provides file storage by key, and generate key for file storage.

"""

import os
import cPickle
import uuid
from flux.constants import user_filebase
from flux.models import Task

def write_pickle(data, filename):
    f = open(filename, 'wb')
    cPickle.dump(data, f)
    f.close()

def read_pickle(name):
    f = open(name, 'rb')
    return cPickle.load(f)
    f.close()

class USL:
    __hivemind = {}     # Singleton Pattern, Borg implementation

    """ Initial version: use file system to store all the file index"""
    def __init__(self):
        self.__dict__ = self.__hivemind

    def initialize(self):
        file_storage = user_filebase + 'file_storage.pk'
	if os.path.exists(file_storage):
            self.storage = read_pickle(file_storage)
        else:
            self.storage = {}
            write_pickle(data = self.storage, filename = file_storage)
        self.__hivemind = self.__dict__

    """ Create a key and a file handler mapping"""
    def create(self, namespace):
        file_storage = user_filebase + 'file_storage.pk'
        u = uuid.uuid1()
        str_uuid = str(u)
        self.storage[str_uuid] = namespace
        write_pickle(data = self.storage, filename = file_storage)
        f = open(user_filebase + namespace + "/" + str_uuid, "w")
        f.close()
        return str_uuid

    """ Return the file handler. the client will close this file handler"""
    def get(self, key):
        if not self.storage.has_key(key):
            print "no such file"
            return None
        else:
            namespace = self.storage[key]
            f = open(user_filebase + namespace + "/" + key, 'r+') # read and write
            return f

    """ Given a key, remove """
    def delete(self, key):
        if self.storage.has_key(key):
            namespace = self.storage[key]
            if os.path.exists(user_filebase + namespace + "/" + key):
                os.remove(user_filebase +  namespace + "/" + key)
            del(self.storage[key])
            write_pickle(data = self.storage, filename = user_filebase + 'file_storage.pk')

if __name__ == "__main__":
    u = USL()
    u.initialize()
    key = u.create("dfba")
    f = u.get(key)
    if f:
        print f
        f.write("hello")
        f.close()
    u.delete(key)
