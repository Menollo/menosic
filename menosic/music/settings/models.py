# menosic/music/settings/models.py
from django.contrib.auth.models import User
from django.db import models


class MusicSettings(models.Model):
    ORDERING_CHOICES = (
        ('sortname', 'By Artist (sortname)'),
        ('name', 'By Artist (full)'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    ordering = models.CharField(
        max_length=20,
        choices=ORDERING_CHOICES,
        default=ORDERING_CHOICES[0][0]
    )

    @classmethod
    def get(cls, user):
        if type(user) == type(User):
            pk = user.pk
        else:
            pk = user
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return None
        try:
            obj = cls.objects.get(user__pk=pk)
        except cls.DoesNotExist:
            obj = cls(user=user)
        return obj
