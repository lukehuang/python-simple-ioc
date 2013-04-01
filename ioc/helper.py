# vim: set fileencoding=utf-8 :

import ioc.component
import ioc.loader
import logging

def is_scalar(value):
    return isinstance(value, (str))

def is_iterable(value):
    return isinstance(value, (dict, list))

def get_keys(arguments):
    if isinstance(arguments, (list)):
        return range(len(arguments))

    if isinstance(arguments, (dict)):
        return arguments.iterkeys()

    return []

class Dict(object):
    def __init__(self, data):
        self.data = data

    def get(self, name, default=None):
        data = self.data
        for name in name.split("."):
            if name in data:
                data = data[name]

            else:
                return default

        return data

    def get_dict(self, name, default=None):
        default = default or {}
        value = self.get(name, default)
        if not isinstance(value, Dict):
            value = Dict(value)

        return value

    def get_int(self, name, default=None):
        return int(self.get(name, default))

    def all(self):
        return self.data
        
    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]     

def build(files, logger=None, parameters=None):

    if not logger:
        logger = logging.getLogger('ioc')

    if not parameters:
        parameters = {}

    container_builder = ioc.component.ContainerBuilder(logger=logger)
    
    loaders = [
        ioc.loader.YamlLoader()
    ]

    logger.debug("Loading files")
    for file in files:
        logger.debug("Search loader for file %s" % file)
        for loader in loaders:
            if not loader.support(file):
                continue

            logger.debug("Found loader %s for file %s" % (loader, file))
            loader.load(file, container_builder)

    container = ioc.component.Container()

    for name, value in parameters.iteritems():
        container_builder.parameters.set(name, value)

    container_builder.build_container(container)

    return container