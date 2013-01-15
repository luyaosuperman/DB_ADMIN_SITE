from django.core.management.base import BaseCommand, CommandError
from db_survey.model_gather_data import *

class Command(BaseCommand):
    def handle(self,*args, **options):
        gather_table_data()
