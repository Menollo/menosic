from django.core.management.base import BaseCommand
from music import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        for collection in models.Collection.objects.all():
            collection.scan()
