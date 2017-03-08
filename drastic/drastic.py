import inspect
from collections import defaultdict


#######################
# Constants
#######################

nonable = 'nonable'


#######################
# Disable/Enable
#######################

_enabled = True

def disable():
    """ Disable all drastic behaviours. """

    global _enabled
    _enabled = False

def enable():
    """ Enable all drastic behaviours. """

    global _enabled
    _enabled = True
    

#######################
# Exceptions
#######################

class ReturnTypeError(TypeError):
    """ Exception raised when a function returns a value of incorrect type. """

    def __init__(self,
        func_name: "name of the function",
        expected: "expected types or 'nonable' keyword",
        returned: "returned value"):
        """ Initialize the exception. """
        
        expected_types = "', '".join(t.__name__ for t in expected if isinstance(t, type))
        error = "Return type of function '{0}' is incorrect: "
        error += "expected '{1}' but '{2}' returned."
        error = error.format(func_name, expected_types, returned.__name__)
        TypeError.__init__(self, error)


class ArgumentTypeError(TypeError):
    """ Exception raised when a function argument has an incorrect type. """

    def __init__(self,
        func_name: "name of the function",
        arg_name: "name of the argument",
        expected: "expected types or 'nonable' keyword",
        received: "value of the argument"):
        """ Initialize the exception. """

        expected_types = "', '".join(t.__name__ for t in expected if isinstance(t, type))
        error = "Argument '{0}' of function '{1}' is incorrect: "
        error += "excepted '{2}' but '{3}' received."
        error = error.format(arg_name, func_name, expected_types, received.__name__)
        TypeError.__init__(self, error)


class AnnotationError(Exception):
    """ Exception raised when the annotation is incorrect. """


#######################
# Utils
#######################

def _type_ok(
    value: "value to check",
    expected: "expected types or 'nonable' keyword"):
    """ Returns True if type of value is one of expected. """

    types = tuple(t for t in expected if isinstance(t, type))
    nullable = 'nonable' in expected
    return isinstance(value, types) or (nullable and value is None)


def _to_tuple(
    value: "value to wrap into a tuple"):
    """ Convert a single value to tuple. """
    
    return value if isinstance(value, tuple) else (value,)


#######################
# @init decorator
#######################

def strict(
    func: "the function to check"):
    """ Decorator to check arguments and return types. """

    def checker(
        *args: "arguments of the function",
        **kwargs: "dict of arguments"):
        """ Function checking arguments and return types. """

        if not _enabled:
            return func(*args, **kwargs)
            
        funcname = func.__name__
        spec = inspect.getfullargspec(func)

        # Arguments check
        if args and not spec.args == ['self']:
            i = 1 if spec.args[0] == 'self' else 0
            for name, value in zip(spec.args[i:], args[i:]):
                if name in spec.annotations:
                    expected = _to_tuple(spec.annotations[name])
                    if not _type_ok(value, expected):
                        raise ArgumentTypeError(funcname, name, expected, type(value))

        result = func(*args, **kwargs)

        # Return check
        if 'return' in spec.annotations:
            expected = _to_tuple(spec.annotations['return'])
            if not _type_ok(result, expected):
                raise ReturnTypeError(funcname, expected, type(result))

        return result
    return checker

#######################
# @init decorator
#######################

# Method to add to the class when 'boolean' in keywords
def _bool(self):
    return bool(getattr(self, type(self)._varbool))

# Methods to add to the class when 'number' in keywords
def _int(self):
    return int(getattr(self, type(self)._varnumber))
def _float(self):
    return float(getattr(self, type(self)._varnumber))

# Method to add to the class when 'string' in keywords
def _str(self):
    obj_name = type(self).__name__
    values = ('{0}={1}'.format(field, getattr(self, field)) for field in type(self)._varstr)
    return '<{0}: {1}>'.format(obj_name, ', '.join(values))

# Methods to add to the class when 'container' in keywords
def _len(self):
    return len(getattr(self, type(self)._varitems))
def _getitem(self, key):
    return getattr(self, type(self)._varitems)[key]
def _setitem(self, key, value):
    getattr(self, type(self)._varitems)[key] = value
def _delitem(self, key):
    del getattr(self, type(self)._varitems)[key]
def _iter(self):
    return iter(getattr(self, type(self)._varitems))
def _reversed(self):
    return reversed(getattr(self, type(self)._varitems))
def _contains(self, item):
    return item in getattr(self, type(self)._varitems)

# Methods to add to the class when 'compare' in keywords
def _eq(self, other):
    varcmp = type(self)._varcmp
    return getattr(self, varcmp) == getattr(other, varcmp)
def _ne(self, other):
    varcmp = type(self)._varcmp
    return getattr(self, varcmp) != getattr(other, varcmp)
def _lt(self, other):
    varcmp = type(self)._varcmp
    return getattr(self, varcmp) < getattr(other, varcmp)
def _le(self, other):
    varcmp = type(self)._varcmp
    return getattr(self, varcmp) <= getattr(other, varcmp)


class Object:
    """ Wraps the object to initialize. """

    # All existing keywords
    all_keywords = ('nonable', 'local', 'private', 'boolean', 'number', 'string', 'container', 'compare')
    
    # Keywords incompatible with the 'local' keyword
    local_incompatible = ('private', 'boolean', 'number', 'string', 'container', 'compare')
    uniques = ('boolean', 'number', 'container', 'compare')
    
    def __init__(self,
        obj: "object to initialize"):
        """ Constructor. """

        self.obj = obj
        self.type = type(obj)
        self.name = type(obj).__name__
        self.keywords = set()


    def add_argument(self,
        argument: "argument to add"):
        """ Adds an argument to the object and the methods that use this argument. """

        self.check_consistency(argument)
        if not hasattr(self.type, '_initialized'):
            if 'private' in argument.keywords:
                self.set_private(argument)
            if 'boolean' in argument.keywords:
                self.add_tobool(argument)
            if 'number' in argument.keywords:
                self.add_tonumber(argument)
            if 'string' in argument.keywords:
                self.register_tostring(argument)
            if 'container' in argument.keywords:
                self.add_container_methods(argument)
            if 'compare' in argument.keywords:
                self.add_comparison_methods(argument)
            
        setattr(self.obj, argument.name, argument.value)


    def finalize(self):
        """ Finalizes the object. """

        self.add_tostring()
        self.type._initialized = True


    def check_consistency(self,
        argument: "we check the consistency between the keywords of this argument and the others"):
        """ Check the consistency of keywords. """

        if 'local' in argument.keywords:
            incompatibles = [k for k in argument.keywords if k in Object.local_incompatible]
            if incompatibles:
                error = "'local' is incompatible with '{0}'.".format("', '".join(incompatibles))
                raise AnnotationError(error)
        uniques = argument.keywords.intersection(Object.uniques)
        error_keywords = uniques.intersection(self.keywords)
        if error_keywords:
            error = "'{0}' should be used once.".format("', '".join(error_keywords))
            raise AnnotationError(error)
        self.keywords.update(argument.keywords)


    def set_private(self,
        argument: "argument to set to private"):
        """ Rename the argument as private. """

        argument.name = '_{0}__{1}'.format(self.name, argument.name)


    def add_tobool(self,
        argument: "bool() will use this argument"):
        """ Adds the method to cast the object to boolean. """

        self.type.__bool__ = _bool
        self.type._varbool = argument.name


    def add_tonumber(self,
        argument: "int() and float() will use this argument"):
        """ Adds the methods to cast the object to number. """

        self.type.__int__ = _int
        self.type.__float__ = _float
        self.type._varnumber = argument.name
    

    def register_tostring(self,
        argument: "str() will use this argument among others"):
        """ Adds the argument to the list of arguments to display in the string representation. """

        if not hasattr(self.type, '_varstr'):
            self.type._varstr = [argument.name]
        else:
            self.type._varstr.append(argument.name)


    def add_container_methods(self,
        argument: "container methods will use this collection"):
        """ Adds the methods to emulate a container. """

        self.type.__getitem__ = _getitem
        self.type.__setitem__ = _setitem
        self.type.__delitem__ = _delitem
        self.type.__iter__ = _iter
        self.type.__reversed__ =  _reversed
        self.type.__contains__ = _contains
        self.type._varitems = argument.name


    def add_comparison_methods(self,
        argument: "comparison methods will use this argument"):
        """ Adds the methods for comparison. """

        self.type.__eq__ = _eq
        self.type.__ne__ = _ne
        self.type.__lt__ = _lt
        self.type.__le__ = _le
        self.type._varcmp = argument.name


    def add_tostring(self):
        """ Adds the method to cast the object to string representation. """

        if hasattr(self.type, '_varstr'):
            self.type.__str__ = _str


class Argument():
    """ Represents an argument of the constructor. """

    def __init__(self,
        name: "name of the argument",
        value: "value of the argument",
        annotations: "annotations for this argument"):
        """ Constructor. """

        self.name, self.value = name, value
        self.types, self.keywords = tuple(), set()
        annotations = _to_tuple(annotations)
        for annotation in annotations:
            if isinstance(annotation, type):
                self.types += (annotation,)
            elif isinstance(annotation, str):
                self.keywords = set(annotation.split())
        
        self.check_type()


    def check_type(self):
        """ Compare the type of the argument with the expected. """

        if self.types:
            nullable = self.value is None and 'nonable' in self.keywords
            if not (nullable or isinstance(self.value, self.types)):
                raise ArgumentTypeError('__init__', self.name, self.types, type(self.value))


def init(
    constructor: "constructor of the object"):
    """ Decorator for object auto-initialization. """

    def __init(
        *args: "arguments to convert to fields",
        **kwargs: "dict of arguments"):
        """ Initializes the object. """

        if _enabled:
        
            spec = inspect.getfullargspec(constructor)
            arguments = list(args)
            if len(arguments) < len(spec.args):
                arguments += spec.defaults[len(arguments) - len(spec.args):]

            annotations = defaultdict(lambda: None, spec.annotations)
            
            obj = Object(arguments[0])
            for name, value in zip(spec.args[1:], arguments[1:]):
                obj.add_argument(Argument(name, value, annotations[name]))
            obj.finalize()

        return constructor(*args, **kwargs)
    return __init
