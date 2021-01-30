from django.db import models


class IntegerParams(models.Model):
    name = models.CharField(max_length=50)
    value = models.IntegerField(verbose_name='Value')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    