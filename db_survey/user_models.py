from django.db import models
import MySQLdb
from datetime import datetime
from datetime import time
from datetime import timedelta
from db_survey.models import *
import time

########################################################
#Custom Managers
class db_user_manager(models.Manager):
    def get_user(self, cluster_id = 0):
        #get user list in [[id,desc],...] form
        l = []
        if cluster_id = 0:
            dict = self.all()
        else:
            dict = self.filter(belong_to_cluster = cluster_id)
        for item in dict:
           item=str(item)
           _db_name = item.split(":")[0]
           cluster_item = db_cluster.objects.get(db_name = _db_name)
           cluster_id = cluster_item.id
           p = self.get( belong_to_cluster = cluster_id , username = item.split(":")[1].split('@')[0], host_ip = item.split(":")[0].split('@')[1] , is_deleted = False)
           l.append([int(p.id),str(p)])
        return l
    def insert_user(self, new_belong_to_cluster , new_username, new_host_ip):
        #insert a new user to the DB, if not exist. Return the object of created user
        obj, created =  self.get_or_create(belong_to_cluster = new_belong_to_cluster, username = new_username, host_ip = new_host_ip,
                                           defaults = {'user_def' : "", "is_new_added" : True, "is_deleted" : False})
        return obj

class user_privilege_manager(models.Manager):
    def get_user_privilege(self, belong_to_user_id)
        #return the privilege of certain user_id, in [[id, privilege], ...] form
        l = []
        for item in self.filter(belong_to_user = belong_to_user_id):
            l.append([item.id , item.privilege])
        return l
    def insert_privilege(self, belong_to_user_id,new_privilege):
        #Should be added later
        affected_schema = ""
        affected_table = ""
        affected_sp = ""
        obj, created =  self.get_or_create(belong_to_user = belong_to_user_id, privilege = new_privilege,
                                           defaults = {"privilege" : new_privilege, "affected_schema" : affected_schema, "affected_table" : affected_table, "affected_sp" : affected_sp,
                                                       "is_new_added" : True, "is_deleted" : False})
        return obj
        
class user_privilege_history_manager(modles.Manager):
    def get_user_privilege_history(self) :
    l = []
    dict = self.all()
    for item in dict:
        p = self.get(id = item.split("#")[0])
        l.append([p.id,str(p)])
    return l


########################################################
class db_user(models.Model):
    belong_to_cluster = models.ForeignKey(db_cluster)
    username = models.CharField(max_length=100)
    host_ip = models.CharField(max_length=15)
    user_def = models.CharField(max_length=100)

    is_new_added = models.BooleanField() #True: if the item is newly added; False: This item is added and commented already
    is_deleted = models.BooleanField()   #False: this item is still in use; True: This column is disappeared

    objects = models.Manager()
    custom_manager = db_user_manager()

    def __unicode__(self):
        return belong_to_cluster.db_name + ':' + self.username +'@'+ self.host_ip

class user_privilege(models.Model):
    belong_to_user = models.ForeignKey(db_user)
    privilege = models.CharField(max_length=500)
    affected_schema = models.CharField(max_length=100) #Not a foreign key since the privilege will still there after table deleted
    affected_table = models.CharField(max_length=100)  #Also, not a foreign key
    affected_sp = models.CharField(max_length=100)

    is_new_added = models.BooleanField() #True: if the item is newly added; False: This item is added and commented already
    is_deleted = models.BooleanField()   #False: this item is still in use; True: This column is disappeared

    def __unicode__(self):
        return self.belong_to_user + self.privilege

class user_privilege_history(models.Model):
    username = models.CharField(max_length=100)
    host_ip = models.CharField(max_length=15)
    db_cluster = models.CharField(max_length=100)
    action = models.CharField(max_length=100) #(add, remove)
    privilege_entry = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s#%s:%s@%s  %s  %s" % (self.id,self.db_cluster , self.username , self.host_ip , action , privilege_entry)
