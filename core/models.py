from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE)


class Type(models.Model):
    name = models.CharField(max_length=50)