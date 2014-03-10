from music import models
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        for collection in models.Collection.objects.all():
            collection.scan()
