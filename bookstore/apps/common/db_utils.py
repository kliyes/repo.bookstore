#coding=utf-8

from django.db import connection

#cur = connection.cursor()
#
#def queryMany(sql, count):
#    cur.execute(sql)
#    return cur.fetchmany(count)
#
#def queryAll(sql, params):
#    cur.execute(sql, params)
#    return cur.fetchall()
#
#def queryOne(sql):
#    cur.execute(sql)
#    return cur.fetchone()

def sql(querySet):
    '''获取查询SQL'''
    return querySet.query
    
    
    