#!/usr/ali/bin/python
# coding=utf-8

'''Implements a database api to houyi, houyidb and houyiregiondb.

Example 0: Create connection:

a. Create a readonly local houyidb:

    houyidb = Houyidb()

b. Create a read/write local houyidb:

    houyidb = Houyidb(read_only = False)

c. Create a auto connect connection

    houyidb = Houyidb(auto_connect = True)

d. Create a read/write houyidb of cluster AYXXX:

    houyidb = Houyidb(cluster = 'AYXXX', read_only = False)

e. Create a read/write houyidb of region cn-hangzhou-x:

    houyidb = Houyidb(cluster = 'cn-hangzhou-x', read_only = False)

f. Set timeout for create connection, default is 3

    houyidb = Houyidb(timeout = 3)

Example 1: Query SQL

a. Use execute() method to execute query sql:

    db.execute('select * from ip')

    # Get only the first two rows
    db.get_rows(2)
    # result like [('10.10.0.1', 'my'), ..]

    # Get the next two rows, but each row record is a dict
    db.get_rows(2, is_dict = True)
    # result like [{'address':'10.10.0.1', 'name': 'my'}, ..]

b. Use query() method to execute query sql directly:

    # The query() method will get the result rows immediately
    db.query('select * from ip', size = 2, is_dict = True)

c. Use split_query() method to split long query into small ones:

   # Assume that the name_list's length is 10000
   # See the docstring of split_query() for more details
   db.split_query('select address from ip', 'name', name_list)

Example 2: Insert SQL

a. Insert a new record into ip table:

    db.execute("insert into ip('address','name') values('192.168.0.1','vm-xxx')")

    # If auto commit set to false, call commit() method manually
    db.commit()

b. Insert multi-records into ip table:

    db.executemany("insert into ip('address','name') values(%s,%s)", [
            ('192.168.0.1', 'vm-xxx'),
            ('192.168.0.2', 'vm-yyy'),
            ('192.168.0.3', 'vm-zzz')])
    db.commit()

Note: db.multi_insert is an alias for executemany method.
See test_main() method for more examples.
'''

from database import DB


class Mydb(DB):
    '''A simple query interface of houyidb.'''
    def __init__(self, read_only = True, auto_commit = False,
                 timeout = 5, auto_connect = False, max_idle_time = 28800):
        '''Initialize the Mydb object.'''
        # Get the database parameters
        args = {'host':'127.0.0.1', 'user':'root','passwd':'lovesqcc','db':'goodcode','port':3306,'charset':'utf8'}

        # Set extra connection parameters
        args['connect_timeout'] = timeout
        args['auto_commit'] = auto_commit
        args['max_idle_time'] = max_idle_time
        args['auto_connect'] = auto_connect

        DB.__init__(self, **args)



class Systemdb(DB):
    '''A simple query interface of Systemdb.'''
    def __init__(self, read_only = True,
                 auto_commit = False, timeout = 5, auto_connect = False,
                 max_idle_time = 28800):
        '''Initialize the Systemdb object.'''
        # Get the database parameters
        args = {'host':'127.0.0.1', 'user':'root','passwd':'lovesqcc','db':'mysql','port':3306,'charset':'utf8'}

        # Set extra connection parameters
        args['connect_timeout'] = timeout
        args['auto_commit'] = auto_commit
        args['max_idle_time'] = max_idle_time
        args['auto_connect'] = auto_connect

        DB.__init__(self, **args)

