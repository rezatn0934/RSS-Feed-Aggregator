from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rssfeeds.serializers import XmlLinkSerializer, ChannelSerializer, PodcastSerializer, NewsSerializer
from .models import Channel, XmlLink, Podcast, News
from .utils import parse_podcast_data, create_or_update_categories


# Create your views here.


class XmlLinkViewSet(CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = XmlLinkSerializer
    queryset = XmlLink.objects.all()
