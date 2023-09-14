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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        xml_link = serializer.save()

        [data, model] = parse_podcast_data(xml_link)

        categories = create_or_update_categories(data.get('channel_data')['categories'])

        channel_data = data.get('channel_data')['data']
        channel, created = Channel.objects.get_or_create(xml_link=xml_link, defaults=channel_data)
        if not created:
            for key, value in channel_data.items():
                setattr(channel, key, value)
            channel.save()

        channel.category.set(categories)

        podcast_data = data.get('podcast_data')
        podcast_items = [model(channel=channel, **item) for item in podcast_data]
        model.objects.bulk_create(podcast_items)

        return Response('ok', status=status.HTTP_201_CREATED)


class ChannelViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'last_update', 'description', 'author']
    ordering_fields = ['id', 'title', 'last_update']


class PodcastViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = PodcastSerializer
    queryset = Podcast.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'pub_Date', 'description', 'explicit']
    ordering_fields = ['id', 'title', 'pub_Date']


class NewsViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = NewsSerializer
    queryset = News.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'pub_Date']
    ordering_fields = ['id', 'title', 'pub_Date']
