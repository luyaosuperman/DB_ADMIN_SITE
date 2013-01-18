from django.contrib import admin
#from polls.models import Poll
#from polls.models import Choice

from db_survey.models import *
from db_survey.user_models import *

#class ChoiceInline(admin.TabularInline):
#   model = Choice
#    extra = 3
#
#class PollAdmin(admin.ModelAdmin):
#    fieldsets = [
#        (None,               {'fields': ['question']}),
#        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
#    ]
#    inlines = [ChoiceInline]
#    list_display = ('question', 'pub_date', 'was_published_recently')
#    list_filter = ['pub_date']
#    search_fields = ['question']
#    date_hierarchy = 'pub_date'
#
#admin.site.register(Poll, PollAdmin)

class db_column_admin(admin.ModelAdmin):
    list_display = ('id','belong_to_table','column_name','column_type','column_allow_null','column_key_type','column_default_value','column_extra','column_def')
    search_fields = ('column_name',)
    list_filter = ('belong_to_table',)
    ordering = ('id',)

class db_dictoionary_admin(admin.ModelAdmin):
    list_display = ('dict_entry','dict_explain')
    ordering = ('id',)

class db_key_admin(admin.ModelAdmin):
   list_display = ('id','belong_to_table','table_key_def','key_def')
   list_filter = ('belong_to_table','table_key_def')
   ordering = ('id',)


admin.site.register(db_cluster)
admin.site.register(db_schema)
admin.site.register(db_table)
admin.site.register(db_column,db_column_admin)
admin.site.register(db_table_keys,db_key_admin)
admin.site.register(db_key_type)
admin.site.register(db_dictoionary,db_dictoionary_admin)
admin.site.register(db_user)
admin.site.register(user_privilege)
