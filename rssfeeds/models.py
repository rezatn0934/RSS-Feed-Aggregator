from django.db import models

# Create your models here.
from core.models import Type, Category


class XmlLink(models.Model):
    xml_link = models.URLField(unique=True)
    rss_type = models.ForeignKey(Type, on_delete=models.PROTECT)

