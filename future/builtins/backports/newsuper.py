'''
This module provides a super() function in Python 2 that mimics the
behaviour of super() in Python 3. It is designed to be used as follows:

    from __future__ import division, absolute_import, print_function
    from future.builtins import super

And then, for example:

    class VerboseList(list):
        def append(self, item):
            print('Adding an item')
            super().append(item)        # new simpler super() function

Importing this module on Python 3 has no effect.

This is based on (i.e. almost identical to) Ryan Kelly's magicsuper
module here:

    https://github.com/rfk/magicsuper.git

Excerpts from Ryan's docstring:

  "Of course, you can still explicitly pass in the arguments if you want
  to do something strange.  Sometimes you really do want that, e.g. to
  skip over some classes in the method resolution order.
  
  "How does it work?  By inspecting the calling frame to determine the
  function object being executed and the object on which it's being
  called, and then walking the object's __mro__ chain to find out where
  that function was defined.  Yuck, but it seems to work..."
'''

import sys

from future.utils import PY3


_builtin_super = super

_SENTINEL = object()

def super(typ=_SENTINEL, type_or_obj=_SENTINEL, framedepth=1):
    '''Like builtin super(), but capable of magic.

    This acts just like the builtin super() function, but if called
    without any arguments it attempts to infer them at runtime.
    '''
    #  Infer the correct call if used without arguments.
    if typ is _SENTINEL:
        # We'll need to do some frame hacking.
        f = sys._getframe(framedepth)    

        try:
            # Get the function's first positional argument.
            type_or_obj = f.f_locals[f.f_code.co_varnames[0]]
        except (IndexError, KeyError,):
            raise RuntimeError('super() used in a function with no args')
        
        try:
            # Get the MRO so we can crawl it.
            mro = type_or_obj.__mro__
        except AttributeError:
            try:
                mro = type_or_obj.__class__.__mro__
            except AttributeError:
                raise RuntimeError('super() used with a non-newstyle class')
        
        #   A ``for...else`` block?  Yes!  It's odd, but useful.
        #   If unfamiliar with for...else, see: 
        #
        #       http://psung.blogspot.com/2007/12/for-else-in-python.html
        for typ in mro:
            #  Find the class that owns the currently-executing method.
            for meth in typ.__dict__.values():
                if not isinstance(meth, type(super)):
                    continue
                if meth.func_code is f.f_code:
                    break   # Aha!  Found you.
            else:
                continue    #  Not found! Move onto the next class in MRO.
            break    #  Found! Break out of the search loop.
        else:
            raise RuntimeError('super() called outside a method')
    
    #  Dispatch to builtin super().
    if type_or_obj is not _SENTINEL:
        return _builtin_super(typ, type_or_obj)
    return _builtin_super(typ)


def superm(*args, **kwds):
    f = sys._getframe(1)
    nm = f.f_code.co_name
    return getattr(super(framedepth=2),nm)(*args, **kwds)


if PY3:
    import builtins
    super = builtins.super
    __all__ = []
else:
    __all__ = ['super']
