# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render, get_object_or_404,render_to_response
from db_survey.models import *
from db_survey.model_method import *
from django.template import RequestContext
from db_survey.forms import *
from db_survey.user_view import *

def index(request):
    message = 'Hello!'
    return HttpResponse(message)

def search(request):
    errors = []
    if 'q' in request.GET:
        name=str(request.GET['q'])
        if not name:
            errors.append('Empty search item')
        elif len(name) > 5:
            errors.append('String too long')
        else:
            tables = db_table.objects.filter(table_name=name)
            return render_to_response('db_survey/search_result.html',
                {'tables': tables, 'query': name})
    return render_to_response('db_survey/search_form.html', {'errors' : errors})

#def search_form(request):
#    return render_to_response('db_survey/search_form.html')

#def search(request):
#    if 'q' in request.GET:
#        message = 'You searched for: %s' % request.GET['q']
#    else:
#        message = 'You submitted an empty form.'
#    return HttpResponse(message)

def edit_column_def(request):
    result = []
    modified = False
    if request.method == "POST":
        form = edit_column_form(request.POST)
        if form.is_valid() and form.clean_def():
            cd = form.cleaned_data
            new_col_name = cd['col_name']
            new_col_def = cd['col_def']
            modified = True
            return render_to_response('db_survey/edit_column_def.html',{ 'form':form , 'modified' : modified , 'new_col_name' : new_col_name , 'new_col_def' : new_col_def },context_instance=RequestContext(request)) 
            #return HttpResponseRedirect('db_survey/edit_column_def_done/')
    else:    
        form = edit_column_form(initial = {'col_name' : default_col_name_text,'col_def':default_col_def_text})
        return render_to_response("db_survey/edit_column_def.html",{'form':form,'modified' : modified})

def display_all(request):
    #message = 'Hello!'
    #return HttpResponse(message)
    [display_items,display_keys] = get_full_list_db()
    return render_to_response('db_survey/display_all.html',{ 'display_items' : display_items , 'display_keys' : display_keys })

def display_cluster_list(request):
    #url_list is dict, with the key (and possible other items) is the item in display_list, which is a list
    if request.method == "GET" and 'target_cluster' in request.GET:
        cluster_id = int(request.GET['target_cluster'])
        [display_items,display_keys] = get_full_list_db(cluster_id)
        [schema_dict, schema_display_list] = get_schema_list_of_a_cluster(cluster_id)
        return render_to_response('db_survey/display_all.html',{ 'display_items' : display_items , 'display_keys' : display_keys , 
                                                                 "schema_dict":schema_dict,"schema_display_list":schema_display_list})
    else:
        [cluster_dict, display_list] = get_cluster_list_db()
        return render_to_response('db_survey/display_cluster.html', {'cluster_dict': cluster_dict, 'display_list': display_list})

def modify_cluster_list(request):
    if request.method == "GET" and 'target_cluster' in request.GET: # from list goto the edit cluster PAGE
        cluster_id = int(request.GET['target_cluster'])
        cluster_item = db_cluster.objects.get(id=cluster_id)
        cluster_info_key_list = cluster_item.get_display_fields(for_modify = True)
        cluster_info_dict = dict()

        for key_item in cluster_info_key_list:
            cluster_info_dict[key_item] = str(getattr(cluster_item,key_item))
        form = edit_cluster_form(initial = cluster_info_dict)
        [schema_dict, schema_display_list] = get_schema_list_of_a_cluster(cluster_id)
        return render_to_response('db_survey/edit_cluster.html', {'form_cluster':form, "schema_dict":schema_dict,"schema_display_list":schema_display_list, 'source_cluster_id':cluster_id}) 
                                                                      #{'cluster_info_dict':cluster_info_dict , 'cluster_info_key_list':cluster_info_key_list})
    elif request.method == "POST":# on edit cluster PAGE, finished editing
        form = edit_cluster_form(request.POST)
        if form.is_valid():
             form_dict = form.cleaned_data
        else:
             return HttpResponse('Failed because form is broken <a href="/db_survey/modify_cluster_list/>Go back to the previous Screen<a>')
        cluster_id = int(form_dict['id'])
        cluster_item= db_cluster.objects.get(id = cluster_id)
        cluster_info_key_list = cluster_item.get_display_fields(for_modify = True)
        for key_item in cluster_info_key_list:
            setattr(cluster_item, key_item, form_dict[key_item])
        cluster_item.save()
        return HttpResponse('Done <a href="/db_survey/modify_cluster_list/?target_cluster=%s">Go back to the previous Screen<a>' % cluster_id)
             
    else:# GOTO the List Page
        [cluster_dict, display_list] = get_cluster_list_db()
        return render_to_response('db_survey/modify_cluster_list.html', {'cluster_dict': cluster_dict, 'display_list': display_list})

def edit_schema(request):
    #message = 'Hello!'
    #return HttpResponse(message)
    if request.method == "GET" and 'target_schema' in request.GET:#Goto the edit schema page
        source_cluster_id = int(request.GET['source_cluster_id'])
        schema_id = int(request.GET['target_schema'])
        schema_item = db_schema.objects.get(id = schema_id)
        schema_info_key_list = schema_item.get_display_fields(for_modify = True)
        schema_info_dict = dict()

        for key_item in schema_info_key_list:
            schema_info_dict[key_item] = str(getattr(schema_item,key_item))
        form = edit_schema_form(initial  = schema_info_dict)
        [table_dict, table_display_list] = get_table_list_of_a_schema(schema_id)
        return render_to_response('db_survey/edit_schema.html', {'form_schema':form , 'source_cluster_id':source_cluster_id, 'source_schema_id' : schema_id, 'table_dict': table_dict,'table_display_list': table_display_list})
    elif request.method == "POST":
        form = edit_schema_form(request.POST)
        if form.is_valid():
             form_dict = form.cleaned_data
        else:
             return HttpResponse('Failed because form is broken <a href="/db_survey/modify_cluster_list/>Go back to the previous Screen<a>')
        schema_id = int(form_dict['id'])
        schema_item = db_schema.objects.get(id = schema_id)
        schema_info_key_list = schema_item.get_display_fields(for_modify = True)
        for key_item in schema_info_key_list:
            setattr(schema_item, key_item, form_dict[key_item])
        schema_item.save()
        source_cluster_id = schema_item.belong_to_cluster.id
        return HttpResponse('Done <a href="/db_survey/edit_schema/?target_schema=%s&source_cluster_id=%s">Go back to the previous Screen<a>' % (schema_id,source_cluster_id))

def edit_table(request):
    if request.method == 'GET' and 'source_schema_id' in request.GET:
        schema_id = int(request.GET['source_schema_id'])
        schema_item = db_schema.objects.get(id = schema_id)
        l = []
        table_list = schema_item.table_belong_to_schema
        for table in table_list:
            table_form_list = []
            table_id = table[0]
            table_name = table[1]
            table_item = db_table.objects.get(belong_to_schema = schema_id, id = table_id, is_deleted = False)
            table_info_key_list = table_item.get_display_fields(for_modify = True)
            table_info_dict = dict()
            for key_item in table_info_key_list:
                table_info_dict[key_item] = str(getattr(table_item,key_item))
            form = edit_table_form(initial = table_info_dict)
            table_form_list.append(form)
            ####add key
            ####add column
            column_list = table_item.column_belong_to_table
            for column in column_list:
                column_id = column[0]
                column_name = column[1]
                column_item = db_column.objects.get(belong_to_table = table_id, id = column_id)
                column_info_key_list = column_item.get_display_fields(for_modify = True)
                column_info_dict = dict()
                for key_item in column_info_key_list:
                    column_info_dict[key_item] = str(getattr(column_item,key_item))
                form = edit_column_form(initial = column_info_dict)
                table_form_list.append(form)

            l.append(table_form_list)
        source_cluster_id = schema_item.belong_to_cluster.id
        return render_to_response('db_survey/edit_table.html', {'table_form_list': l, 'source_schema_id': schema_id, 'source_cluster_id': source_cluster_id })
    elif request.method == 'POST':
        #form = edit_table_form(request.POST)
        #if form.is_valid():
        #     form_dict = form.cleaned_data
        if 'table_name' in request.POST.keys():
            #edit table
            form = edit_table_form(request.POST)
            if form.is_valid():
                form_dict = form.cleaned_data
            else:
                return HttpResponse('Failed because form is broken')
            table_id = int(form_dict['id'])
            table_item = db_table.objects.get(id = table_id)
            table_info_key_list = table_item.get_display_fields(for_modify = True)
            for key_item in table_info_key_list:
                setattr(table_item,key_item,form_dict[key_item])
            table_item.save()
            source_schema_id = table_item.belong_to_schema.id
            return HttpResponse('Done <a href="/db_survey/edit_table/?target_table=%s&source_schema_id=%s">Go back to the previous Screen<a>' % (table_id ,source_schema_id))
        elif 'column_name' in request.POST.keys():
            #edit column
            form = edit_column_form(request.POST)
            if form.is_valid():
                form_dict = form.cleaned_data
            else:
                return HttpResponse('Failed because form is broken')
            column_id = int(form_dict['id'])
            column_item = db_column.objects.get(id = column_id)
            column_info_key_list = table_column.get_display_fields(for_modify = True)
            for key_item in column_info_key_list:
                setattr(column_item,key_item,form_dict[key_item])
            column_item.save()
            source_schema_id = column_item.belong_to_table.belong_to_schema.id
            source_table_id = column_item.belong_to_table.id
            return HttpResponse('Done <a href="/db_survey/edit_table/?target_table=%s&source_schema_id=%s">Go back to the previous Screen<a>' % (source_table_id ,source_schema_id))
