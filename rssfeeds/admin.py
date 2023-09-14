from django.contrib import admin
from .models import Channel, Podcast, News, XmlLink
# Register your models here.


admin.site.register(XmlLink)
admin.site.register(Podcast,)
admin.site.register(News)
admin.site.register(Channel)
