from django.db import models

class UUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'max_length': 32,
            'blank': True,
            'null': True,
            })
        super(UUIDField, self).__init__(*args, **kwargs)
