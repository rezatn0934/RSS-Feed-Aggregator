from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('rssfeeds', views.XmlLinkViewSet)
router.register('channels', views.ChannelViewSet)
router.register('podcasts', views.PodcastViewSet)
router.register('news', views.NewsViewSet)
router.register('search_podcast', views.PodcastDocumentView, basename='search_podcast')
router.register('search_channel', views.ChannelDocumentView, basename='search_channel')
router.register('search_news', views.NewsDocumentView, basename='search_news')

app_name = 'rssfeeds'
urlpatterns = [
    path('update_rssfeeds/', views.UpdateRSSFeedsView.as_view(), name='update_rssfeeds'),
    path('', include(router.urls)),
]
