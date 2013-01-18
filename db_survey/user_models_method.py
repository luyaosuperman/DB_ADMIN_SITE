from django.db import models
import MySQLdb
from datetime import datetime
from datetime import time
from datetime import timedelta
from db_survey.user_models import *
import time

def update_user_privilege():
    #Gather user privilege from differenet database
    cluster_list = db_cluster.custom_manager.get_cluster()  #[[id,name],...]
    for cluster in cluster_list:
        cluster_name = cluster[1]
        cluster_item = db_cluster.objects.get(db_name = cluster_name)
        cluster_db_master_ip = cluster_item.db_master_ip
        cluster_id = cluster_item.id
        user_list = cluster_item.get_user_from_mysql()#[[user,host_ip],...]
        for user_entry in user_list:
            username = user_entry[0]
            host_ip = user_entry[1]
            db_user_item = db_user.custom_manager.insert_user(cluster_item, username, host_ip)
            user_id = db_user_item.id
            privilege_list = db_user_item.get_user_privilege_from_mysql(cluster_db_master_ip) #[privilege line 1,line 2, ... ]
            for privilege_line in privilege_list:
                user_privilege.custom_manager.insert_privilege(db_user_item,privilege_line)
            
