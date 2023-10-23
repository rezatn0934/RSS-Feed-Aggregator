from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from accounts.authentication import JWTAuthentication
from .mixins import AuthenticationMixin
from .serializers import (
    ChannelSerializer,
    NewsSerializer,
    XmlLinkSerializer,
    ChannelDocumentSerializer,
    PodcastSerializer,
    PodcastDocumentSerializer,
    NewsDocumentSerializer
)
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_RANGE,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_CONTAINS,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    CompoundSearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet

from .documents import ChannelDocument, PodcastDocument, NewsDocument

from .models import Channel, XmlLink, Podcast, News
from .tasks import xml_link_creation, update_rssfeeds


class XmlLinkViewSet(AuthenticationMixin, CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin,
                     GenericViewSet):
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


    Permissions:
        - POST, DELETE: Admin access required.
        - GET: AllowAny access for listing News items.
    """

    serializer_class = XmlLinkSerializer
    queryset = XmlLink.objects.all()

    def create(self, request, *args, **kwargs):
        xml_link = request.data.get('xml_link')
        rss_type = request.data.get('rss_type')
        obj, created = XmlLink.objects.get_or_create(xml_link=xml_link, rss_type_id=rss_type)
        xml_link_creation.delay(obj.xml_link)
        return Response({'message': _('Your request is processing')}, status=status.HTTP_201_CREATED)


class UpdateRSSFeedsView(AuthenticationMixin, APIView):

    def get(self, request):
        update_rssfeeds.delay()

        return Response({'message': _('RSS Feeds have been updated')}, status=status.HTTP_200_OK)


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
    authentication_classes = (JWTAuthentication,)
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
            items_serializer = PodcastSerializer(items, many=True, context={'request': request})
        elif hasattr(channel, 'news_set') and (len(channel.news_set.all()) > 0):
            items = channel.news_set.all()
            items_serializer = NewsSerializer(items, many=True, context={'request': request})
        if items:
            data = {
                'channel': self.get_serializer(channel).data,
                'items': items_serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'message': _('channel has no item')},
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


class PodcastDocumentView(BaseDocumentViewSet):
    """The BookDocument view."""

    document = PodcastDocument
    serializer_class = PodcastDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = (
        'subtitle',
        'title',
        'description',
        'channel.title',
    )

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_QUERY_CONTAINS,
            ],
        },
        'title': 'title.raw',
        'pub_date': 'pub_date',
        'channel': 'channel.title.raw',
        'subtitle': 'subtitle.raw',
        'description': 'description.raw',
        'explicit': 'explicit'
    }

    ordering_fields = {
        'id': 'id',
        'title': 'title.raw',
        'channel': 'channel.title.raw',
        'pub_date': 'pub_date',
    }

    ordering = ('id', 'title', 'pub_date')


class NewsDocumentView(BaseDocumentViewSet):
    """The BookDocument view."""

    document = NewsDocument
    serializer_class = NewsDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]

    search_fields = {
        'channel.title': {'fuzziness': 'AUTO'},
        'title': {'fuzziness': 'AUTO'},
    }
    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_QUERY_CONTAINS,
            ],
        },
        'title': 'title.raw',
        'pub_date': 'pub_date',
        'channel.title': 'channel.title.raw',
    }

    ordering_fields = {
        'id': 'id',
        'title': 'title.raw',
        'channel.title': 'channel.title.raw',
        'pub_date': 'pub_date',
    }

    ordering = ('id', 'title', 'pub_date')


class ChannelDocumentView(BaseDocumentViewSet):
    """The BookDocument view."""

    document = ChannelDocument
    serializer_class = ChannelDocumentSerializer
    lookup_field = 'id'
    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]

    search_fields = {
        'subtitle': {'fuzziness': 'AUTO'},
        'title': {'fuzziness': 'AUTO'},
        'description': {'fuzziness': 'AUTO'},
        'author': {'fuzziness': 'AUTO'},
        'category.name': {'fuzziness': 'AUTO'},
    }

    filter_fields = {
        'id': {
            'field': '_id',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
                LOOKUP_QUERY_CONTAINS,
            ],
        },
        'title': 'title.raw',
        'subtitle': 'subtitle.raw',
        'description': 'description.raw',
        'language': 'language',
        'author': 'author.raw',
        'category': 'category.name',
        'owner': 'owner',
        'last_update': 'last_update',
    }

    ordering_fields = {
        'id': 'id',
        'title': 'title.raw',
        'last_update': 'last_update',
    }

    ordering = ('id', 'title', 'last_update')
