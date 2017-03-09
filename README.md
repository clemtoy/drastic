# drastic
Reduce the size of your Python3 code and increase its robustness.

## Introduction
Drastic uses annotations for type checking and object auto-initialization. It provides the following decorators.

**@strict**
- control arguments of a function or method
- control returned value

**@init**
- control arguments of a constructor
- add some special methods to the class
- auto-initialize the object with the given values

## Installation

***This package works only with Python3*** since annotations are Python3 features.

Drastic is on the [PyPI](https://pypi.python.org/pypi/drastic) repository. Thus, you can install it using `pip` or `easy_install`:

```
pip install drastic
```
or

```
easy_install drastic
```

## @strict decorator

Let's begin with a simple example:

```Python
from drastic import strict

@strict
def hello(name: str):
    print("Hello " + name)
```

The annotation `str` specifies that `name` should be a string. If it is not, an `ArgumentTypeError` is raised. It also works with parameters:

```Python
@strict
def hello(name: str="world"):
    print("Hello " + name)
```

Guess what! You can check the returned value:

```Python
@strict
def value_of(obj: MyObject) -> int:
    return obj.value
```

It will raise a `ReturnTypeError` if the returned value is not a `int`.
To allow multiple types, just use a tuple like this:

```Python
@strict
def display(value: (int, str)):
    print("The value is {0}".format(value))
```

Sometimes, you will like to allow `None` values:

```Python
from drastic import strict, nonable

@strict
def display(value: (int, str, nonable)):
    print("The value is {0}".format(value))
```


## @init decorator

Python object initialization is very verbose:

```Python
class User:
    """ Represents an user. """

    def __init__(self, firstname, lastname, sex, age, weigth, height):
        """ Initializes an user. """

        self.firstname = firstname
        self.lastname = lastname
        self.sex = sex
        self.age = age
        self.weight = weight
        self.height = height
```

It doesn't match the level of laziness of any Python developer. Using Drastic shorten drastically your code:

```Python
from drastic import init

class User:
    """ Represents an user. """

    @init
    def __init__(self, firstname, lastname, sex, age, weigth, height):
        """ Initializes an user. """
```

No, I don't forgot anything. The `@init` decorator auto-initializes the object!

`@init` also performs type checking on arguments as `@strict` does:

```Python
class User:
    """ Represents an user. """

    @init
    def __init__(self,
        firstname: str="John",
        lastname: str="Doe",
        sex: str="Unknown",
        age: int,
        weigth: (int, float),
        height: (int, float)):
        """ Initializes an user. """
```

Use a string of keywords to add more initialization constraints:

```Python
class User:
    """ Represents an user. """

    @init
    def __init__(self,
        firstname: (str, 'string')="John",
        lastname: (str, 'string')="Doe",
        sex: str="Unknown",
        age: (int, 'compare number'),
        weigth: (int, float, 'private nonable'),
        height: (int, float)):
        """ Initializes an user. """
```

These are the available keywords:
- `nonable`: argument value can be `None`
- `local`: do not add the argument as an object property
- `private`: add the argument as a private property
- `boolean`: property to use when casting the object to `bool`
- `number`: property to use when casting the object to `int` or `float`
- `string`: use these properties in the string representation of the object (`str(user)` would return `"<User: firsname=John, lastname=Doe>"`)
- `container`: use this property to emulate a container
- `compare`: use this property when comparing two objects

## Enable/Disable

By default, drastic is enabled.
You can disable/enable using `drastic.disable()` and `drastic.enable()`.
