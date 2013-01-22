from django.conf.urls import patterns, url

#from polls import views
from db_survey import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    #url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    # ex: /polls/5/results/
    #url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    # ex: /polls/5/vote/
    #url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    #url(r'^search-form/$', views.search_form),
    url(r'^search/$', views.search),
    url(r'^edit_column_def/$', views.edit_column_def),
    url(r'^display_cluster_list/$', views.display_cluster_list),
    url(r'^display_all/$', views.display_all),
    url(r'^modify_cluster_list/$', views.modify_cluster_list),
    url(r'^edit_schema/$', views.edit_schema),
    url(r'^edit_table/$', views.edit_table),
    url(r'^modify_user_privilege/$', views.modify_user_privilege)
   
)
