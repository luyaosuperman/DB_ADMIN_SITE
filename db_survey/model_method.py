from django.db import models
import MySQLdb
from datetime import datetime
from datetime import time
from datetime import timedelta
import time
from db_survey.models import *

def get_cluster_list_db():
    db_cluster_list = db_cluster.custom_manager.get_cluster() #[[id,name],...]
    cluster_dict = dict()
    display_list = []
    for item in db_cluster_list:
        cluster_dict[item[1]]=item[0]
        display_list.append(item[1])
    return [cluster_dict, display_list]

def get_schema_list_of_a_cluster(cluster_id):
    schema_dict = dict()
    schema_display_list = []
    cluster_item = db_cluster.objects.get(id = cluster_id)
    for item in cluster_item.schema_belong_to_cluster:
        schema_dict[item[1]]=item[0]
        schema_display_list.append(item[1])
    return [schema_dict, schema_display_list]

def get_table_list_of_a_schema(schema_id):
    table_dict = dict()
    table_display_list = []
    schema_item = db_schema.objects.get(id = schema_id)
    for item in schema_item.table_belong_to_schema:
        table_dict[item[1]]=item[0]
        table_display_list.append(item[1])
    return [table_dict, table_display_list]

def update_column():
    cluster_list = db_cluster.custom_manager.get_cluster()  #[[id,name],...]
    for cluster in cluster_list:
        cluster_id = cluster[0]
        cluster_name = cluster[1]
        cluster_item = db_cluster.objects.get(id = cluster_id)
        cluster_db_master_ip = cluster_item.db_master_ip
        cluster_db_backup_ip = cluster_item.db_backup_ip
        schema_list = cluster_item.get_schema_from_mysql()
        #get schema to delete schema that no longer exists
        current_schema_list = [d[1] for d in db_schema.custom_manager.get_schema_from_cluster_id(cluster_id)]
        for schema_to_delete in (set(current_schema_list) - set(schema_list)):
            db_schema.objects.get(belong_to_cluster = cluster_id, schema_name = schema_to_delete).delete()
            print "schema %s in cluster %s no longer exists" % (schema_to_delete, cluster_name)
        for schema in schema_list:
            schema_item = db_schema.custom_manager.insert_schema(schema,cluster_item)
            schema_id = schema_item.id
            tables = schema_item.get_table_belong_to_schema_from_mysql(cluster_db_master_ip)
            current_tables = [d[1] for d in db_table.custom_manager.get_table_from_schema_id(schema_id)]
            for table_to_delete in (set(current_tables) - set([d[0] for d in tables])):
                print "table_to_delete:", table_to_delete
                db_table.objects.get(belong_to_schema = schema_id, table_name = table_to_delete).delete()
            for table in tables:#[table_name, primary_key]
                table_item = db_table.custom_manager.insert_table(table[0],schema_item,table[1])
                table_id = table_item.id
                columns = table_item.get_column_belong_to_table_from_mysql(cluster_db_master_ip)
                current_columns = [d[1] for d in db_column.custom_manager.get_column_from_table_id(table_id)]
                for column_to_delete in (set(current_columns) - set([d['COLUMN_NAME'] for d in columns])):
                    db_column.objects.get(belong_to_table = table_id, column_name = column_to_delete).delete()
                for column in columns:
                    column_item = db_column.custom_manager.insert_column(column, table_item)

                keys = table_item.get_key_belong_to_table_from_mysql(cluster_db_master_ip)
                current_keys = db_table_keys.custom_manager.get_key_from_table_id(table_id)
                for key_to_delete in (set([d[1] for d in current_keys]) - set(keys)):
                    print "key_to_delete:", key_to_delete
                    db_table_keys.objects.get(belong_to_table = table_id, table_key_def = key_to_delete).delete()
                for key in keys:
                    key_item = db_table_keys.custom_manager.insert_key(table_item,key)

    print "Done!"


def get_full_list_db(cluster_id = 0):
    l = []
    display_keys = []
    temp_dict = dict()
    first_round = True
    cluster_list = db_cluster.custom_manager.get_cluster(cluster_id)  #[[id,name],...]
    for cluster in cluster_list:
        cluster_id = cluster[0]
        cluster_name = cluster[1]
        cluster_item = db_cluster.objects.get(id = cluster_id)
        schema_list = cluster_item.schema_belong_to_cluster

        display_items = cluster_item.get_display_fields()
        for display_item in display_items:
            temp_dict[display_item] = str(getattr(cluster_item,display_item))
            temp_dict[display_item + '_rowspan'] = cluster_item.column_count
            if first_round == True:
                display_keys.append(display_item)
####################
        for schema in schema_list: 
            schema_id = schema[0]
            schema_name = schema[1]
            schema_item = db_schema.objects.get(belong_to_cluster = cluster_id,id = schema_id, is_deleted = False)
            table_list = schema_item.table_belong_to_schema 

            display_items = schema_item.get_display_fields()
            for display_item in display_items:
                temp_dict[display_item] = str(getattr(schema_item,display_item))
                temp_dict[display_item + '_rowspan'] = schema_item.column_count
                if first_round == True:
                    display_keys.append(display_item)
####################
            for table in table_list:
                table_id = table[0]
                table_name = table[1]
                table_item = db_table.objects.get(belong_to_schema = schema_id, id = table_id, is_deleted = False)
                column_list = table_item.column_belong_to_table
            
                display_items = table_item.get_display_fields()
                for display_item in display_items:
                    temp_dict[display_item] = str(getattr(table_item,display_item))
                    temp_dict[display_item + '_rowspan'] = table_item.column_count
                    if first_round == True:
                        display_keys.append(display_item)
                ####display_key
                key_list = table_item.key_belong_to_table
                display_item = ["table_key_def"] # key is not materialized, so can't get display_list from item
                if key_list:
                    key_string = ''
                    for key in key_list:
                       key_string += key[1] + ' <br> '
                    temp_dict["table_key_def"] = key_string
                    temp_dict["table_key_def" + '_rowspan'] = table_item.column_count
                else:
                    temp_dict["table_key_def"] = ''
                    temp_dict["table_key_def" + '_rowspan'] = table_item.column_count
                if first_round == True:
                    display_keys.append("table_key_def")
               
####################
                for column in column_list:
                    column_id = column[0]
                    column_name = column[1]
                    column_item = db_column.objects.get(belong_to_table = table_id, id = column_id, is_deleted = False)
                    #temp_dict = dict()

                    for display_item in column_item.get_display_fields():
                        temp_dict[display_item] = str(getattr(column_item,display_item))
                        temp_dict[display_item + '_rowspan'] = 1
                        if first_round == True:
                            display_keys.append(display_item)
###################Dict
                    temp_dict['dictionary'] = column_item.get_dict_string()
                    temp_dict['dictionary' + '_rowspan'] = 1
                    if first_round == True:
                        display_keys.append('dictionary')
                    first_round = False
                    l.append(temp_dict)
                    temp_dict = dict() #clear the dict
    #display_keys.append('non_exist_key')
    return [l,display_keys]
