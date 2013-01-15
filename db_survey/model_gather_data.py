from django.db import models
import MySQLdb
from datetime import datetime
from datetime import time
from datetime import timedelta
import time
from db_survey.models import *
#import rrdtool
from rrdtool import create, graph,update
import os
import time
import threading
import random

random.seed()

rrd_data_path = '/home/garadmin/django/1/mysite/db_survey/rrd/'
rrd_image_path = '/home/garadmin/django/1/mysite/db_survey/rrd/image/'

def create_or_get_rrd_database(check_item,cluster_name,schema_name='',table_name=''):
    full_file_path = rrd_data_path + check_item + '.' + cluster_name
    if schema_name != '':
        full_file_path += '.' + schema_name
        if table_name != '':
            full_file_path += '.' + table_name
    full_file_path += '.rrd'
    if os.path.exists(full_file_path) == False:
        create(full_file_path, 
                       '--start',str(int(time.time())), 
                       'DS:%s:GAUGE:3600:U:U' % (check_item), 
                       'RRA:AVERAGE:0.5:1:8760') #24*365
    return full_file_path

def get_rrd_pic_path(check_item,cluster_name,schema_name,table_name,days = 1):
    full_file_path = create_or_get_rrd_database(check_item,cluster_name,schema_name,table_name)

    full_image_path = rrd_image_path + check_item + '.' + cluster_name
    if schema_name != '':
        full_image_path += '.' + schema_name
        if table_name != '':
            full_image_path += '.' + table_name
    full_image_path += '.png'
    #Reference
    #rrdtool graph target.png --start 1357622790 --end 1357623120 DEF:mymem=target.rrd:mem:AVERAGE LINE1:mymem#FF0000
    graph(str(full_image_path),
                  '--start', str(int(time.time()) - 86400* days ),
                  '--end',   str(int(time.time())),
                  '--vertical-label', 'Rows',
                  '--title', 'Table Row Count of past %s days' % days,
                  str('DEF:myvariable=%s:%s:AVERAGE' % (full_file_path, check_item)),
                  'LINE1:myvariable#FF0000')

    return full_image_path.split('/')[-1]
    
    

def get_table_rows(cluster_backup_ip, schema_name, table_name, rrd_database_file):
    #thread_count += 1
    #try:
        print "inside thread now!"
        conn_src = connect_mysql(cluster_backup_ip)
        cursor_src = conn_src.cursor()
        #need to exclude the view
        sql = "show table status in %s where Name='%s'" % (schema_name, table_name)
        cursor_src.execute(sql)
        if cursor_src.fetchone()[1] != None: #Detected a view, [1] is the Engine type
            sql = "select count(*) from %s.%s" % (schema_name,table_name)
            cursor_src.execute(sql)
            rows = str(cursor_src.fetchone()[0])
        else:
            rows = 0

        timestamp = int(time.time())
        update(rrd_database_file,'%s:%s' % (timestamp,rows))
        print rrd_database_file, '%s:%s' % (timestamp,rows)

        conn_src.close()
    #except:
    #    pass
    #thread_count -= 1
    #return rows

def test():
   print 'Hello'


def myfunc(i):
    print "sleeping 5 sec from thread %d" % i
    time.sleep(5)
    print "finished sleeping from thread %d" % i

def invoke_thread():
    for i in range(10):
        t = threading.Thread(target=myfunc, args=(i,))
        t.start()

def gather_table_data():
    thread_count = 0
    print "start timestamp: ", time.time()
    cluster_list = db_cluster.custom_manager.get_cluster()  #[[id,name],...]
    for check_item in check_item_list:
        for cluster in cluster_list:
            cluster_id = cluster[0]
            cluster_name = cluster[1]
            cluster_item = db_cluster.objects.get(id = cluster_id)
            cluster_backup_ip = cluster_item.db_backup_ip
            schema_list = cluster_item.schema_belong_to_cluster
####################
            for schema in schema_list: 
                schema_id = schema[0]
                schema_name = schema[1]
                schema_item = db_schema.objects.get(belong_to_cluster = cluster_id,id = schema_id, is_deleted = False)
                table_list = schema_item.table_belong_to_schema 
####################
                for table in table_list:
                    table_id = table[0]
                    table_name = table[1]
                    table_item = db_table.objects.get(belong_to_schema = schema_id, id = table_id, is_deleted = False)
                    
                    if check_item == 'table_rows':
                    ####check the number of rows in a table, then store it in rrdtool
                        rrd_database_file = create_or_get_rrd_database(check_item,cluster_name,schema_name,table_name)
                        t = threading.Thread(target=get_table_rows, 
                                         args=(cluster_backup_ip, schema_name, table_name, rrd_database_file))
                        t.start()
                        thread_count +=1
                        while thread_count > 10:
                            time.sleep(3)
                            print 'thread_count: ' , thread_count
                            thread_count = 0
                        #threading.Thread(target = test, name = 'thread' + str(time.time()) + str(random.randint(1,999)))
                        
    print "finished time", time.time()
