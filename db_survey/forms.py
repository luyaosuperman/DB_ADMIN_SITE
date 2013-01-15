from django import forms
from django.forms import ModelForm

default_col_name_text = 'put column name here'
default_col_def_text = 'put column defination here'

class edit_column_form(forms.Form):
    col_name = forms.CharField(max_length=100,label='Colnumn name')
    col_def = forms.CharField(widget=forms.Textarea,max_length=100,label='Column Defination')

    def clean_def(self):
        col_name = self.cleaned_data['col_name']
        col_def = self.cleaned_data['col_def']
        if col_name == default_col_name_text or col_def == default_col_def_text:
            raise forms.ValidationError("Nothing found here")
            return False
        else:
            return True

class edit_cluster_form(forms.Form):
    id = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    db_name = forms.CharField(max_length=100, label =    "Name of this DB Cluster")
    db_master_ip = forms.CharField(max_length=15,label = "DB Master IP")
    db_backup_ip = forms.CharField(max_length=15,label = "DB Backup Slave IP")
    db_def = forms.CharField(max_length=100, label =     "Description of this DB Cluster",widget=forms.Textarea)


class edit_schema_form(forms.Form):
    id = forms.CharField(max_length=10)
    schema_name = forms.CharField(max_length=100, label = "Name of this Schema")
    schema_def = forms.CharField(max_length=100, label = "Description of this DB Schema",widget=forms.Textarea)

class edit_table_form(forms.Form):
    id = forms.CharField(max_length=10)
    table_name = forms.CharField(max_length=100, label = "Name of this Table")
    table_primary_keys = forms.CharField(max_length=100, label = "Primary Key of this Table")
    table_def = forms.CharField(max_length=100, label = "Description of this Table",widget=forms.Textarea)

class edit_column_form(forms.Form):
    id = forms.CharField(max_length=10)
    column_name = forms.CharField(max_length=100, label =    "Name of the Column")
    column_type = forms.CharField(max_length=100, label =    "Data Type of the Column")
    column_allow_null = forms.BooleanField(label = "If this Column allow Null value?")
    column_key_type = forms.ChoiceField(choices = (('PRI','PRI'),('UNI', 'UNI'), ('MUL' , 'MUL')))
    column_default_value = forms.CharField(max_length=100, label =    "Default value of the Column")
    column_extra = forms.CharField(max_length=100, label =    "Extra Property of the Column")
    column_def = forms.CharField(max_length=100, label =    "Defination of the Column")

class edit_dict_form(forms.Form):
    id = forms.CharField(max_length=10)
    dict_entry = forms.CharField(max_length=100, label =    "Dictionary Entry")
    dict_explain = forms.CharField(max_length=100, label =    "Explanination Entry")
    
