from __future__ import absolute_import
from cloudfiles import get_connection
from cloudfiles.errors import NoSuchContainer, NoSuchObject
from dictcloud import common

class RemoteObject(common.RemoteObject):
    def __init__(self, obj):
        self.obj = obj
        self.value = None

    def as_string(self):
        if self.value is None:
            self.value = self.obj.read()
        return self.value


class dictcloud(common.DictsLittleHelper):
    def __init__(self, *args, **kwargs):
        print self.connection_args, self.connection_kwargs, "###"*10
        self.connection = get_connection(*self.connection_args, **self.connection_kwargs)
        try:
            self.container = self.connection.get_container(self.key)
        except NoSuchContainer:
            self.container = self.connection.create_container(self.key)
        for key, value in kwargs:
            self[key] = value

    def __setitem__(self, key, value):
        self.container.create_object(key).write(value)

    def __delitem__(self, key):
        self.container.delete_object(key)

    def __getitem__(self, k):
        try:
            return RemoteObject(self.container.get_object(k))
        except NoSuchObject:
            raise KeyError(k)

    def __iter__(self):
        for key in self.container.get_objects():
            yield key.name

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False
        

def factory(container_key, *args, **kwargs):
    class CFDictCloud(dictcloud):
        connection_args = args 
        connection_kwargs = kwargs 
        key = container_key
    return CFDictCloud
