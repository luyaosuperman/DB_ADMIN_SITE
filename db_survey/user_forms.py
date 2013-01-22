from django import forms
from django.forms import ModelForm

class new_privilege_form(forms.Form):
    new_privilege_string = forms.CharField(max_length=1000, label = "new privilege")

class delete_user_form(forms.Form):
    confirm_string = forms.CharField(max_length=15, label = "Type [Delete User] here to confirm the delete user action")

