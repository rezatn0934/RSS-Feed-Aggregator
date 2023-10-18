from django.contrib import admin
from .models import Like, Comment, Subscription, BookMark, Recommendation, Notification
# Register your models here.


admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Subscription)
admin.site.register(BookMark)
admin.site.register(Recommendation)
admin.site.register(Notification)
