from django.db import models
import MySQLdb
from datetime import datetime
from datetime import time
from datetime import timedelta
import time
import sys
sys.path.append("/root/db_access_list/")

from  db_access_list import * #db_username db_password db_port of the db access, under /root/db_access_list

from model_gather_data import *
#from user_models_method import *


check_item_list = ['table_rows']


#db_username = ''
#db_password = ''
#db_port = 0

def connect_mysql(db_ip):
##############Connect Mysql
    source_db_host= db_ip
    source_db_user=db_username
    source_passwd =db_password
    source_db_port=db_port
    try:
        conn_src =MySQLdb.connect(host = source_db_host , user = source_db_user , passwd = source_passwd , db = 'mysql', port = source_db_port , connect_timeout = 2,charset='utf8')
    except:
        print str(datetime.now()),"Connection to source DB %s failed" % ( db_ip )
        return False

    #sql = "flush tables"
    #cursor_src = conn_src.cursor()
    #cursor_src.execute(sql)
    return conn_src

# Create your models here.
class db_cluster_manager(models.Manager):
    def get_cluster(self, cluster_id = 0):
        l = []
        if cluster_id == 0:
            dict = self.all()
        else:
            dict = self.filter(id = cluster_id)
        for item in dict:
           item=str(item)
           p = self.get(db_name = item, is_deleted = False)
           l.append([int(p.id),str(p.db_name)])
        return l

    
        
class db_schema_manager(models.Manager):
    def get_schema_from_cluster_id(self,input_id): # get the id and schema name according to CLUSTER ID
        l = []
        for item in self.filter(belong_to_cluster=input_id):
            l.append([item.id , item.schema_name])
        return l
    def insert_schema(self, new_schema_name, new_belong_to_cluster_instance):
        obj, created =  self.get_or_create(belong_to_cluster = new_belong_to_cluster_instance, schema_name = new_schema_name,
                                      defaults = {'is_new_added':True, 'is_deleted':False, 'schema_def':''})
        return obj

class db_table_manager(models.Manager):
    def get_table_from_schema_id(self, input_id): # get the id and table name according to SCHEMA ID
        l = []
        for item in self.filter(belong_to_schema=input_id):
            l.append([item.id , item.table_name])
        return l
    def insert_table(self, new_table_name, new_belong_to_schema_instance, table_primary_keys=''):
        obj, created =  self.get_or_create(belong_to_schema = new_belong_to_schema_instance, table_name = new_table_name,
                              defaults = {'is_new_added':True, 'is_deleted':False, 'table_def':'','table_primary_keys':table_primary_keys})
        if created == True:
            print "Table %s added" % (new_table_name,)
        return obj

class db_table_keys_manager(models.Manager):
    def get_key_from_table_id(self, input_id):
        l = []
        for item in self.filter(belong_to_table=input_id):
            l.append([item.id , item.table_key_def])
        return l
    def insert_key(self, new_belong_to_table_instance, new_table_key_def):
        obj, created =  self.get_or_create(belong_to_table = new_belong_to_table_instance, table_key_def = new_table_key_def,
                                             defaults = {'key_def' : ''})
        return obj
        

class db_column_manager(models.Manager):
    def get_column_from_table_id(self,input_id):
        l = []
        for item in self.filter(belong_to_table=input_id):
            l.append([item.id , item.column_name])
        return l
    def insert_column(self,column,table_instance):
        #l.append({COLUMN_NAME:column[0]},COLUMN_TYPE:column[1],COLUMN_KEY:column[2],COLUMN_DEFAULT:column[3],EXTRA:column[4]})
        column_key = db_key_type.objects.get(key_type_name = column['COLUMN_KEY'])
        obj, created =  self.get_or_create(belong_to_table = table_instance, column_name = column['COLUMN_NAME']
                                     ,defaults = {'column_type': column['COLUMN_TYPE'] ,'column_key_type':column_key, 'column_default_value':column['COLUMN_DEFAULT'],'column_extra':column['EXTRA'],'column_def':''})
        return obj


##############################################################

#class is_edited(models.Model):
#    is_new_added = models.BooleanField(default = True)
#    is_deleted = models.BooleanField(default = False)
#    definition = models.CharField(max_length=100)

class db_cluster(models.Model):
    db_name = models.CharField(max_length=100, unique = 'True')
    db_master_ip = models.CharField(max_length=15)
    db_backup_ip = models.CharField(max_length=15)
    objects = models.Manager()
    custom_manager = db_cluster_manager()
    is_new_added = models.BooleanField()
    is_deleted = models.BooleanField()
    db_def = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.db_name

    def get_display_fields(self, for_modify = False):
        if for_modify == False:
            return ['db_name','db_def','user_list']
        else:
            return ['id','db_name','db_master_ip','db_backup_ip','db_def']
    def get_user_from_mysql(self):
        l = []
        conn_src = connect_mysql(self.db_master_ip)
        cursor_src = conn_src.cursor()
        #get all the user
        sql = """select user,host from mysql.user""";
        cursor_src.execute(sql)
        for user_item in cursor_src.fetchall():
            [user,host_ip] =[user_item[0],user_item[1]]
            l.append([user,host_ip])
        conn_src.close()
        return l #[[user,host_ip],...]

    def get_schema_from_mysql(self):
        l = []
        conn_src = connect_mysql(self.db_master_ip)
        cursor_src = conn_src.cursor()
        ##############Get all the schema
        #sql = "select SCHEMA_NAME from information_schema.SCHEMATA where SCHEMA_NAME not in ('information_schema','performance_schema','system','mysql');"
        sql = "show databases"
        cursor_src.execute(sql)
        for schema in cursor_src.fetchall():
            if schema[0] not in ['information_schema','performance_schema','system','mysql']:
                l.append(str(schema[0]))
        ##############
        conn_src.close()
        return l

    def _get_schema_belong_to_cluster(self):
        _result = self.db_schema_set.all()
        l = []
        for item in _result:
           l.append([item.id,str(item)])
        return l
    schema_belong_to_cluster = property(_get_schema_belong_to_cluster)
    def _column_count(self):
       _columns = 0
       for item in self.schema_belong_to_cluster:
           #print item
           _p = self.db_schema_set.get( belong_to_cluster = self.id , schema_name = item[1] )
           _columns += _p.column_count
       return _columns
    column_count = property(_column_count)
    def _user_list(self):# get the user belong to this cluster
        user_list_string = """<a href=/db_survey/modify_user_privilege/?target_cluster=%s>""" % (self.id,) + "Add new user" + "</a><br>"#should return a string
        conn_src = connect_mysql("10.10.50.161")
        cursor_src = conn_src.cursor()
        for db_user_item in self.db_user_set.all():
            db_master_ip_last_seg=self.db_master_ip.split(".")[-1]
            sql = """select max(timestamp) from sa_db_access_log.user_access_log where user = '%s' and host = '%s' and master_ip like '%%%s'""" % (db_user_item.username, db_user_item.host_ip, db_master_ip_last_seg)
            cursor_src.execute(sql)
            result = cursor_src.fetchone()
            if result[0] == None:
                user_status = "[never seen]"
            elif int(result[0]) < int(time.time()) - 86400*30:
                user_status = "[30+ day not seen]"
            else:
                user_status = ""
            user_list_string += """<a href=/db_survey/modify_user_privilege/?target_cluster=%s&target_user=%s>""" % (self.id, db_user_item.id)  + str(db_user_item.username + "@" + db_user_item.host_ip) + """</a>""" + user_status +"<br>"
        conn_src.close()
        return user_list_string
    user_list = property(_user_list)

class db_schema(models.Model):
    belong_to_cluster = models.ForeignKey(db_cluster)
    schema_name = models.CharField(max_length=100)
    schema_def = models.CharField(max_length=100)
    objects = models.Manager()
    custom_manager = db_schema_manager()
    is_new_added = models.BooleanField() #True: if the item is newly added; False: This item is added and commented already
    is_deleted = models.BooleanField()   #False: this item is still in use; True: This column is disappeared
    def __unicode__(self):
        return self.schema_name

    def get_display_fields(self, for_modify = False):
        if for_modify == False:
            return ['schema_name','schema_def']
        else:
            return ['id','schema_name','schema_def']

    def get_table_belong_to_schema_from_mysql(self, cluster_db_master_ip):
        l=[]
        conn_src = connect_mysql(cluster_db_master_ip)
        cursor_src = conn_src.cursor()
        sql = """show tables in %s """ % (self.schema_name)
        cursor_src.execute(sql)
        for table in cursor_src.fetchall():
            table_instance = []
            table_name = str(table[0])  # How to pickout duplicated? (1) length > 9 (2) right(tablename,8) is number (3) left part is found in the list with similiar item
            duplicated_name = False
            #print len(table_name) > 9, table_name[-8:], table_name[-8:].isdigit(), table_name[:-9]
            if len(table_name) > 9 and table_name[-8:].isdigit():
                for item in l:
                    item = item[0]
                    if len(item) > 9 and item[:-9] == table_name[:-9]:
                        #print table_name , 'duplicated'
                        duplicated_name = True
                        break
                for item in self.table_belong_to_schema:
                    item = item[1]
                    if len(item) > 9 and item[:-9] == table_name[:-9]:
                        #print table_name , 'duplicated'
                        duplicated_name = True
                        break
            if duplicated_name == False: 
                table_instance.append(table_name)
                #Find the primary key of this table
                table_primary_key=""
                sql = """select column_name from information_schema.KEY_COLUMN_USAGE
                       where table_schema = '%s' and table_name = '%s' and constraint_name = 'PRIMARY' order by ordinal_position""" % (self.schema_name,table_name)
                cursor_src.execute(sql)
                for column_name in cursor_src.fetchall():
                    table_primary_key += str(column_name[0]) + ','
                table_instance.append(table_primary_key)
            if table_instance: l.append(table_instance)# it will run ONLY when it is not a duplicated table
        conn_src.close()
        return l

    def _get_table_belong_to_schema(self):
        _result = self.db_table_set.all()
        l = []
        for item in _result:
            l.append([item.id,str(item)])
        return l
    table_belong_to_schema = property(_get_table_belong_to_schema)
    def _column_count(self):
       _columns = 0
       for item in self.table_belong_to_schema:
           #print item
           _p = self.db_table_set.get( belong_to_schema = self.id , table_name = item[1] )
           _columns += _p.column_count
       return _columns
    column_count = property(_column_count)

class db_table(models.Model):
    belong_to_schema = models.ForeignKey(db_schema)
    table_name = models.CharField(max_length=100)
    table_primary_keys = models.CharField(max_length=100)
    table_def = models.CharField(max_length=100)
    objects = models.Manager()
    custom_manager = db_table_manager()
    is_new_added = models.BooleanField()
    is_deleted = models.BooleanField()
    def __unicode__(self):
        return self.table_name

    def get_display_fields(self, for_modify = False):
        if for_modify == False:
            return ['table_name','table_def','last_day_active','last_week_active','last_month_active']
        else:
            return ['id','table_name','table_primary_keys','table_def']

    def get_column_belong_to_table_from_mysql(self,cluster_db_master_ip):
        l=[]
        conn_src = connect_mysql(cluster_db_master_ip)
        cursor_src = conn_src.cursor()
        sql = """select COLUMN_NAME,COLUMN_TYPE,COLUMN_KEY,COLUMN_DEFAULT,EXTRA from information_schema.COLUMNS where TABLE_SCHEMA='%s' and TABLE_NAME = '%s';""" % (self.belong_to_schema.schema_name,self.table_name) 
        cursor_src.execute(sql)
        for column in cursor_src.fetchall():
            if column[3] is None:
                column_default = ''
            else:
                column_default = column[3]

            if column[4] is None:
                column_extra = ''
            else:
                column_extra = column[4]
            l.append({'COLUMN_NAME':column[0],'COLUMN_TYPE':column[1],'COLUMN_KEY':column[2],'COLUMN_DEFAULT':column_default,'EXTRA':column_extra})
            #print column[1]
        conn_src.close()
        return l

    def get_key_belong_to_table_from_mysql(self,cluster_db_master_ip):
        l=[]
        conn_src = connect_mysql(cluster_db_master_ip)
        cursor_src = conn_src.cursor()

        sql = """ show create table %s.%s """ % (self.belong_to_schema.schema_name,self.table_name)
        cursor_src.execute(sql)
        result_list = cursor_src.fetchone()[1].split('\n')
        for item in result_list:
            if 'KEY' in item: l.append(item)
        #sql = """ select distinct constraint_name from information_schema.KEY_COLUMN_USAGE
        #          where table_schema = '%s' and table_name = '%s';""" % (self.belong_to_schema.schema_name,self.table_name)
        #cursor_src.execute(sql)
        #for key in cursor_src.fetchall():
        #    key_name =key[0]
        #    key_defination = ''

        #    sql = """select column_name,referenced_table_schema,referenced_table_name,referenced_column_name from information_schema.KEY_COLUMN_USAGE
        #           where table_schema = '%s' and table_name = '%s' and constraint_name = '%s'  order by ordinal_position;""" % (self.belong_to_schema.schema_name,self.table_name, key_name)
        #    cursor_src.execute(sql)
        #    key_defination += key_name + " : "
        #    for column_item in cursor_src.fetchall():
        #        ####if it is NOT a foreign key
        #        if column_item[1] is None:
        #            key_defination += column_item[0]
        #        ####if it is a FOREIGN KEY
        #        else:
        #            key_defination += column_item[0] + ' REFERENCE: ' + column_item[1]+'.'+column_item[2]+ '.' +column_item[3]
        #    l.append(key_defination)
            
        conn_src.close()
        return l

    def _get_column_belong_to_table(self):
        _result =  self.db_column_set.all()
        l = []
        for item in _result:
            l.append([item.id,str(item)])
        return l
    column_belong_to_table = property(_get_column_belong_to_table)

    def _get_key_belong_to_table(self):
        _result = self.db_table_keys_set.all()
        l = []
        for item in _result:
            l.append([item.id,str(item)])
        return l
    key_belong_to_table = property(_get_key_belong_to_table)
    def _column_count(self):
        return self.db_column_set.count()
    column_count = property(_column_count)

    def _last_active(self,days):
        #Retun the picture path with html tag of the RDD tool pic, in last day
        for check_item in check_item_list:
            table_name = self.table_name
            schema_name = self.belong_to_schema.schema_name
            cluster_name = self.belong_to_schema.belong_to_cluster.db_name
            rrd_pic_path = get_rrd_pic_path(check_item,cluster_name,schema_name,table_name, days)
            return '''<img src="/media/%s" />''' % (rrd_pic_path)

    def _last_day_active(self):
        return self._last_active(1)

    def _last_week_active(self):
        return self._last_active(7)

    def _last_month_active(self):
        return self._last_active(30)

    last_day_active = property(_last_day_active)
    last_week_active = property(_last_week_active)
    last_month_active = property(_last_month_active)


class db_table_keys(models.Model):
    belong_to_table = models.ForeignKey(db_table)
    table_key_def = models.CharField(max_length=300)
    key_def = models.CharField(max_length=100)
    is_new_added = models.BooleanField()
    is_deleted = models.BooleanField()

    objects = models.Manager()
    custom_manager = db_table_keys_manager()

    def __unicode__(self):
        return self.table_key_def
    def get_display_fields(self, for_modify = False):
        if for_modify == False:
            return ['table_key_def','key_def']
        else:
            return ['id','table_key_def','key_def']

class db_key_type(models.Model):
    key_type_name = models.CharField(max_length=10)
    def __unicode__(self):
        return self.key_type_name
    def get_display_fields(self):
        return ['key_type_name']

class db_column(models.Model):
    belong_to_table = models.ForeignKey(db_table)
    column_name = models.CharField(max_length=100)
    column_type = models.CharField(max_length=100)
    column_allow_null = models.BooleanField()
    column_key_type = models.ForeignKey(db_key_type)
    column_default_value = models.CharField(max_length=100)
    column_extra = models.CharField(max_length=100)
    column_def = models.CharField(max_length=100)
    is_new_added = models.BooleanField()
    is_deleted = models.BooleanField()
    
    objects = models.Manager()
    custom_manager = db_column_manager()

    def get_dict_string(self):
        dict_string = ''
        for dict_list in self.dict_belong_to_column:
            dict_item = db_dictoionary.objects.get(id = dict_list[0])
            dict_string += dict_item.dict_entry + ": " + dict_item.dict_explain + "; "
        return dict_string

    def __unicode__(self):
        return self.column_name

    def get_display_fields(self, for_modify = False):
        if for_modify == False:
            return ['column_name','column_type','column_allow_null','column_key_type','column_default_value','column_extra','column_def']
        else:
            return ['id','column_name','column_type','column_allow_null','column_key_type','column_default_value','column_extra','column_def']

    def _get_dict_belong_to_column(self):
        _result = self.db_dictoionary_set.all()
        l = []
        for item in _result:
            l.append([item.id,str(item)])
        return l
    dict_belong_to_column = property(_get_dict_belong_to_column)

class db_dictoionary(models.Model):
    belong_to_column = models.ForeignKey(db_column)
    dict_entry = models.CharField(max_length=100)
    dict_explain = models.CharField(max_length=100)
    #is_new_added = models.BooleanField()
    #is_deleted = models.BooleanField()
    def __unicode__(self):
        return u'%s : %s' % (self.dict_entry,self.dict_explain)
    def get_display_fields(self):
        return ['dict_entry' , 'dict_explain']


