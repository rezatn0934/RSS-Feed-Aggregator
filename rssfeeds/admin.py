from django.contrib import admin
from .models import Channel, Podcast, News, XmlLink
# Register your models here.


admin.site.register(XmlLink)
admin.site.register(News)
admin.site.register(Channel)


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = ['id']
    search_fields = ['id']
