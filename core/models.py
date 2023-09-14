from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='categories')

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=50)