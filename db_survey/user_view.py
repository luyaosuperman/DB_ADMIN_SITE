# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404,render_to_response
from db_survey.models import *
from db_survey.user_models import *
from db_survey.model_method import *
from django.template import RequestContext
from db_survey.user_forms import *

def modify_user_privilege(request):
    if request.method == "GET" and 'target_cluster' in request.GET:
        if 'target_user' in request.GET: #Edit existing user
            modify_user = True
            target_cluster_id = int(request.GET['target_cluster'])
            cluster_item = db_cluster.objects.get(id = target_cluster_id)
            cluster_name = cluster_item.db_name

            user_id = int(request.GET['target_user'])
            db_user_item = db_user.objects.get(id = user_id)
            user_at_host = db_user_item.username + "@" + db_user_item.host_ip
            privilege_list = [d[1] for d in user_privilege.custom_manager.get_user_privilege(user_id)]
            _new_privilege_form = new_privilege_form()
            _delete_user_form = delete_user_form()
            return render_to_response('db_survey/modify_user_privilege.html', 
                                         {'modify_user'         : modify_user,
                                          'privilege_list'      : privilege_list,
                                          'new_privilege_form'  : _new_privilege_form,
                                          'delete_user_form'    : _delete_user_form,
                                          'source_cluster_id'   : target_cluster_id,
                                          'source_cluster_name' : cluster_name,
                                          'user_at_host'        : user_at_host})
        else:#Add new user
            modify_user = False
