from django.urls import path
from . import views

app_name = 'rssfeeds'
urlpatterns = [
    path('xml_link/', views.XmlLinkView.as_view())
]
