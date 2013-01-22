from django.core.management.base import BaseCommand, CommandError
from db_survey.model_method import *

class Command(BaseCommand):
    def handle(self,*args, **options):
        update_column()
