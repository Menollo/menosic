from django.core.management.base import BaseCommand
from music import models


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path', nargs='?', type=str)

    def handle(self, *args, **options):
        for collection in models.Collection.objects.filter(disabled=False):
            collection.scan(options['path'])
