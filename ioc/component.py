# vim: set fileencoding=utf-8 :

import ioc.exceptions
import importlib
import ioc.helper
import re


class Reference(object):
    def __init__(self, id):
        self.id = id
        
class Definition(object):
    def __init__(self, clazz=None, arguments={}, kwargs={}):
        self.klass = clazz
        self.arguments = arguments
        self.kwargs = kwargs
        self.method_calls = []

class ParameterHolder(object):
    def __init__(self, parameters={}):
        self.parameters = parameters

    def __setitem__(self, key, value):
        self.parameters[key] = value

    def __getitem__(self, key):
        if key in self.parameters:
            return self.parameters[key]

        return None

    def __delitem__(self, key):
        del self.parameters[key]

class ParameterResolver(object):
    def __init__(self):
        self.re = re.compile("%%|%([^%\s]+)%")

    def resolve(self, parameter, parameter_holder):
        if not type(parameter) == str:
            return parameter

        if ioc.helper.is_iterable(parameter):
            for key in ioc.helper.get_keys(parameter):
                parameter[key] = self.resolve(parameter[key], parameter_holder)

        else:
            def replace(matchobj):
                if matchobj.group(0) == '%%':
                    return '%'

                return parameter_holder[matchobj.group(1)]
            
            parameter, num = re.subn(self.re, replace, parameter)

        return parameter


class Container(object):
    def __init__(self):
        self.services = {}
        self.parameters = ParameterHolder()
        self.stack = []

    def has(self, id):
        return id in self.services

    def add(self, id, service):
        self.services[id] = service

    def get(self, id):
        if id not in self.services:
            raise ioc.exceptions.UnknownService()

        return self.services[id]

class ContainerBuilder(Container):
    def __init__(self):
        self.services = {}
        self.parameters = ParameterHolder()
        self.stack = []
        self.parameter_resolver = ioc.component.ParameterResolver()

    def build_container(self, container):
        for id, definition in self.services.iteritems():
            self.get_service(id, definition, container)

    def get_class(self, definition):
        class_name = definition.klass.split(".")[-1]
        module_name = ".".join(definition.klass.split(".")[0:-1])

        m = importlib.import_module(module_name)

        return getattr(m, class_name)

    def get_instance(self, klass, definition, container):
        return klass(*self.set_services(definition.arguments, container), **self.set_services(definition.kwargs, container))

    def get_service(self, id, definition, container):
        if container.has(id):
            return container.get(id)

        if id in self.stack:
            raise ioc.exceptions.CyclicReference(" -> ".join(self.stack) + " -> " + id)

        self.stack.append(id)
        instance = self.get_instance(self.get_class(definition), definition, container)
        container.add(id, instance)     
        self.stack.pop()

        return instance

    def set_service(self, value, container):
        if isinstance(value, Reference) and not container.has(value.id):
            return self.get_service(value.id, self.get(value.id), container)

        if isinstance(value, Reference) and container.has(value.id):
            return container.get(value.id)

        if ioc.helper.is_iterable(value):
            return self.set_services(value, container)

        return self.parameter_resolver.resolve(value, self.parameters)

    def set_services(self, arguments, container):
        for pos in ioc.helper.get_keys(arguments):
            arguments[pos] = self.set_service(arguments[pos], container)

        return arguments
 



