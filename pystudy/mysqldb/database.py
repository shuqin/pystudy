#!/usr/ali/bin/python
# coding=utf-8

import re

'''Implements a simple database interface

Example 0: Create connection:

    # Set auto commit to false, default case
    db = DB(auto_commit = False, host = 'x', user = 'x', passwd = 'x', db = 'x')
    # Set auto commit to true
    db = DB(auto_commit = True, host = 'x', user = 'x', passwd = 'x', db = 'x')
    # Set auto connect to true, this will set auto commit to true too
    # This will enable auto connect when the connection is timeout
    db = DB(auto_connect = True, host = 'x', user = 'x', passwd = 'x', db = 'x')

Example 1: Query SQL

a. Use query() method to execute query sql directly:

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
'''

# Can be 'Prototype', 'Development', 'Product'
__status__ = 'Development'
__author__ = 'tuantuan.lv <tuantuan.lv@alibaba-inc.com>'

import sys
import time
import MySQLdb

from storage import Storage

OperationalError = MySQLdb.OperationalError

def _format(sql):
    '''Format the sql.'''
    return ' '.join(sql.split())

class DB():
    '''A simple database query interface.'''
    def __init__(self, auto_commit = False, auto_connect = False,
                 max_idle_time = 28800, **kwargs):
        '''Initialize the DB object.'''
        #
        # Remember the max idle time (default: 28800)
        # You should set this value to mysql option 'wait_timeout'
        #
        # mysql> show variables like 'wait_timeout';
        # +---------------+-------+
        # | Variable_name | Value |
        # +---------------+-------+
        # | wait_timeout  | 28800 |
        # +---------------+-------+
        #
        self.max_idle_time = max_idle_time

        kwargs.setdefault('charset', 'utf8')             # set default charset to utf8
        kwargs['port'] = int(kwargs.get('port', '3306')) # set default port to 3306

        self._db = None                     # MySQLdb connection object
        self._db_cursor = None              # MySQLdb cursor object
        self.cursor = None                  # MySQLdb cursor object, deprecated
        self._db_args = kwargs              # MySQL db connection args
        self._last_use_time = time.time()   # Last active time

        self._auto_connect = auto_connect   # Auto connect when timeout
        self._auto_commit = auto_commit     # Auto commit

        # Open a new mysql connection
        self._reconnect()

    def __del__(self):
        self.close()

    def close(self):
        '''Close the database connection.'''
        if self._db is not None:
            self._db_cursor.close()
            self._db.close()
            self._db = None

    def _reconnect(self):
        '''Close existing connection and re-open a new one.'''
        self.close()
        self._db = MySQLdb.connect(**self._db_args)

        # Override auto commit setting if auto connect is true
        if self._auto_connect:
            self._db.autocommit(True)
        else:
            self._db.autocommit(self._auto_commit)

        self._db_cursor = self._db.cursor()
        self.cursor = self._db_cursor

    def _ensure_connected(self):
        '''Ensure we connect to mysql.'''
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (8 hours by default).
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self._reconnect()

        self._last_use_time = time.time()

    def _cursor(self):
        '''Get the cursor.'''
        if self._auto_connect:
            self._ensure_connected()

        return self._db_cursor

    def execute(self, sql, args = None):
        '''Execute a sql and return the affected row number.

        You should call the get_rows method to fetch the rows manually.
        '''
        cursor = self._cursor()
        return cursor.execute(_format(sql), args)

    def execute_lastrowid(self, sql, args = None):
        '''Execute a sql and return the last row id.

        You should call the get_rows method to fetch the rows manually.
        '''
        cursor = self._cursor()
        cursor.execute(_format(sql), args)

        return cursor.lastrowid

    def executemany(self, sql, args):
        '''Execute a multi-row insert.

        You can use this method to do a multi-row insert:

           c.executemany(
              """INSERT INTO breakfast (name, spam, eggs, sausage, price)
              VALUES (%s, %s, %s, %s, %s)""",
              [
              ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
              ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
              ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
              ] )

        See http://mysql-python.sourceforge.net/MySQLdb.html for more help.
        '''
        cursor = self._cursor()
        return cursor.executemany(_format(sql), args)

    # Execute a multi-row insert, the same as executemany()
    multi_insert = executemany

    def get_rows(self, size = None, is_dict = False):
        '''Get the result rows after executing.'''
        cursor = self._cursor()
        description = cursor.description

        if size is None:
            rows = cursor.fetchall()
        else:
            rows = cursor.fetchmany(size)

        if rows is None:
            rows = []

        if is_dict:
            dict_rows = []
            dict_keys = [ r[0] for r in description ]

            for row in rows:
                dict_rows.append(Storage(zip(dict_keys, row)))

            rows = dict_rows

        return list(rows)

    def query(self, sql, args = None, size = None, is_dict = False):
        '''Execute a query sql and return the rows immediately.'''
        self.execute(sql, args)
        return self.get_rows(size, is_dict)

    # Alias of query() method
    select = query

    def split_query(self, sql, in_attr, in_list, max_cnt = 3000):
        '''Split one long query into many small ones.

        For example, if you want to select the records whose attrname is in
        one long list (larger than 8000) of possible values. If you decide to
        use 'attr in (...)' syntax, the length will exceed the maximum length
        of one sql allowed. In this case you must split the long query into many
        small ones.

        in_attr is the attribute name of in operator, and in_list is the possible
        value list. max_cnt is the maximum count of values in one small query.
        '''
        total = len(in_list)

        start = 0
        end = max_cnt

        result = []

        if re.search(r'\bwhere\b', sql.lower()):
        #if sql.lower().find('where ') != -1 or sql.lower().find('where\n') != -1:
            sql = '%s and %s in %%s' % (sql, in_attr)
        else:
            sql = '%s where %s in %%s' % (sql, in_attr)

        while start < total:
            if end < total:
                in_expr = "('%s')" % "','".join(in_list[start:end])
            else:
                in_expr = "('%s')" % "','".join(in_list[start:])

            result.extend(self.query(sql % in_expr))

            start = end
            end += max_cnt

        return result

    #def get_autoincrement_id(self, tbl):
    #    '''Get the next auto increment id of table.
    #
    #    Return None if the table doesn't have an auto-increment id.
    #    '''
    #    self.execute('SHOW TABLE STATUS LIKE %s', (tbl,))
    #    result = self.get_rows(is_dict = True)

    #    if result[0]:
    #        return result[0]['Auto_increment']
    #    else:
    #        return None

    def commit(self):
        '''Commits the current transaction.'''
        if self._db is not None:
            self._db.commit()

    def rollback(self):
        '''Rollback the last transaction.'''
        if self._db is not None:
            self._db.rollback()

# vim: set expandtab smarttab shiftwidth=4 tabstop=4:
