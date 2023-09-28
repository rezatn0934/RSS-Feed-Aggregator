from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from .mixins import AuthenticationMixin
from .serializers import XmlLinkSerializer, ChannelSerializer, PodcastSerializer, NewsSerializer
from .models import Channel, XmlLink, Podcast, News
from .tasks import xml_link_creation, update_rssfeeds


class XmlLinkViewSet(AuthenticationMixin, CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for managing XmlLinks, Channels, and Podcasts.

    Endpoint: CRUD operations on XmlLinks.
    - Supports creating, retrieving, updating, and deleting XmlLinks.
    - Upon creating a new XmlLink, it also processes associated podcast data.

    Args:
        request (HttpRequest): The HTTP request object containing XmlLink data for creation/update.
        *args: Additional arguments.
        **kwargs: Additional keyword arguments.

    Returns:
        Response: A JSON response indicating success or failure along with appropriate status codes.
    """

    serializer_class = XmlLinkSerializer
    queryset = XmlLink.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        xml_link = serializer.save()
        xml_link_creation.delay(xml_link.xml_link)
        return Response('Your request is processing', status=status.HTTP_201_CREATED)


class UpdateRSSFeedsView(APIView):

    def get(self, request):
        update_rssfeeds.delay()

        return Response('RSS Feeds have been updated', status=status.HTTP_200_OK)


class ChannelViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for listing and retrieving Channels.

    Endpoint: Listing and retrieving Channels.
    - Supports searching and ordering based on title, last_update, description, and author.

    Args:
        None

    Returns:
        Response: A JSON response containing a list of Channels or a single Channel object
        along with appropriate status codes.

    Permissions:
    - GET: AllowAny access for listing Channels.
    """

    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'last_update', 'description', 'author']
    ordering_fields = ['id', 'title', 'last_update']

    def retrieve(self, request, *args, **kwargs):
        channel = self.get_object()
        items_serializer = None
        items = None
        if hasattr(channel, 'podcast_set') and (len(channel.podcast_set.all()) > 0):
            items = channel.podcast_set.all()
            items_serializer = PodcastSerializer(items, many=True)
        elif hasattr(channel, 'news_set') and (len(channel.news_set.all()) > 0):
            items = channel.news_set.all()
            items_serializer = NewsSerializer(items, many=True)
        if items:
            data = {
                'channel': self.get_serializer(channel).data,
                'items': items_serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'channel has no item'},
                status=status.HTTP_404_NOT_FOUND
            )


class PodcastViewSet(AuthenticationMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    ViewSet for listing and retrieving Podcasts.

    Endpoint: Listing and retrieving Podcasts.
    - Supports searching and ordering based on title, pub_Date, description, and explicit flag.

    Args:
        None

    Returns:
        Response: A JSON response containing a list of Podcasts or a single Podcast object
        along with appropriate status codes.

    Permissions:
    - POST, DELETE: Admin access required.
    - GET: AllowAny access for listing News items.
    """

    serializer_class = PodcastSerializer
    queryset = Podcast.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'pub_Date', 'description', 'explicit']
    ordering_fields = ['id', 'title', 'pub_Date']


class NewsViewSet(AuthenticationMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, GenericViewSet):

    """
    ViewSet for listing and retrieving News items.

    Endpoint: Listing and retrieving News items.
    - Supports searching and ordering based on title and pub_Date.

    Args:
        None

    Returns:
        Response: A JSON response containing a list of News items or a single News item
        along with appropriate status codes.

    Permissions:
        - POST, DELETE: Admin access required.
        - GET: AllowAny access for listing News items.
    """

    serializer_class = NewsSerializer
    queryset = News.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'pub_Date']
    ordering_fields = ['id', 'title', 'pub_Date']
