from django.core.management.base import BaseCommand, CommandError
from db_survey.user_models_method import *

class Command(BaseCommand):
    def handle(self,*args, **options):
        update_user_privilege()
