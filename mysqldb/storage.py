#!/usr/ali/bin/python
# coding=utf-8

'''Wrap an existing dict, or create a new one, and access with dot notation

See test_main() for more example.
'''

# Can be 'Prototype', 'Development', 'Product'
__status__ = 'Development'
__author__ = 'tuantuan.lv <tuantuan.lv@alibaba-inc.com>'

# Taken from http://stackoverflow.com/a/12187277
class Storage(object):
    '''Wrap an existing dict, or create a new one, and access with dot notation.

    The attribute _data is reserved and stores the underlying dictionary.

    args:
        d: Existing dict to wrap, an empty dict created by default.
        create: Create an empty, nested dict instead of raising a KeyError.
    '''
    def __init__(self, d = None, create = True):
        '''Initialize storage object.'''
        if d is None: # Create empty storage object
            d = {}
        else: # create as a dictionary?
            d = dict(d)

        # Set storage attributes
        self.__dict__['__storage_data'] = d
        self.__dict__['__storage_create'] = create

    def __getattr__(self, name):
        '''Get the key value.'''
        try:
            value = self.__dict__['__storage_data'][name]

        except KeyError:
            # Create empty storage value if auto-create set to true
            if not self.__dict__['__storage_create']:
                raise

            value = {}
            self.__dict__['__storage_data'][name] = value

        # Create nested dict if the value has items attribute
        if isinstance(value, dict):
            value = Storage(value, self.__dict__['__storage_create'])
            self.__dict__['__storage_data'][name] = value

        return value

    def __setattr__(self, name, value):
        '''Set the storage key to value'''
        self.__dict__['__storage_data'][name] = value

    def __delattr__(self, name):
        '''Delete the storage key.'''
        del self.__dict__['__storage_data'][name]

    def __contains__(self, name):
        '''Check whether the key exists.'''
        return name in self.__dict__['__storage_data']

    def __nonzero__(self):
        '''Check whether the storage is empty.'''
        return bool(self.__dict__['__storage_data'])

    # Defines common dict api
    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    def get(self, name, default = None):
        '''Defines an get method.'''
        return self.__dict__['__storage_data'].get(name, default)

    # Define dictionary like methods
    def keys(self):
        return self.__dict__['__storage_data'].keys()

    def items(self):
        return self.__dict__['__storage_data'].items()

    def values(self):
        return self.__dict__['__storage_data'].values()

    def setdefault(self, name, default = None):
        return self.__dict__['__storage_data'].setdefault(name, default)

    def pop(self, name, *args):
        return self.__dict__['__storage_data'].pop(name, *args)

    def update(self, d, **kwargs):
        return self.__dict__['__storage_data'].update(d, **kwargs)

    def clear(self):
        self.__dict__['__storage_data'].clear()

    def __len__(self):
        return len(self.__dict__['__storage_data'])

    def __iter__(self):
        return self.__dict__['__storage_data'].__iter__()

    def __unicode__(self):
        return u'<Storage %s>' % str(self.__dict__['__storage_data'])

    def __str__(self):
        return '<Storage %s>' % str(self.__dict__['__storage_data'])

    def __repr__(self):
        return '<Storage %s>' % repr(self.__dict__['__storage_data'])

def test_main():
    # Create an empty storage
    d1 = Storage()
    d1.a.b = 1
    d1.b.c = 2

    # Iterate the items in storage object
    for k, v in d1.items():
       print k, v

    # Create a storage in a (key,value) tuple
    d3 = Storage(zip(['a','b','c'], [1,2,3]))
    print d3.a, d3.b, d3.c
    print d3

    # Create a storage from a existing dict
    d4 = Storage({'a':{'b':1}})
    print d4.a.b
    print d4

    # Check the attribute
    d5 = Storage()
    print 'a' in d5 # False
    print d5.a      # create attribute 'a'
    print 'a' in d5 # True
    print d5.get('c')
    print d5.get('d', 3)

    d5 = Storage(create = False)
    print 'a' in d5 # False
    print d5.get('a', 5)
    print d5.a      # raise KeyError
    print 'a' in d5 # False, also

if __name__ == '__main__':
    test_main()
