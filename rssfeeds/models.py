from django.db import models

# Create your models here.
from core.models import Type, Category


class XmlLink(models.Model):
    xml_link = models.URLField(max_length=500, unique=True)
    rss_type = models.ForeignKey(Type, on_delete=models.PROTECT)


class Channel(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    subtitle = models.TextField(null=True, blank=True)
    image = models.URLField(max_length=500, null=True, blank=True)
    author = models.TextField()
    xml_link = models.OneToOneField(XmlLink, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, blank=True)
    owner = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class AbstractRssItem(models.Model):
    title = models.CharField(max_length=250)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    guid = models.CharField(max_length=150)
    pub_date = models.DateTimeField(null=True, blank=True)
    image = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Podcast(AbstractRssItem):
    subtitle = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.CharField(null=True, blank=True)
    audio_file = models.URLField(max_length=500)
    explicit = models.BooleanField(null=True, blank=True)


class News(AbstractRssItem):
    source = models.URLField(max_length=500, null=True, blank=True)
    link = models.URLField(max_length=500)
