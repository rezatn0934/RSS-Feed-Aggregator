
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from interactions.models import Like, BookMark
from .models import XmlLink, Channel, Podcast, News


class XmlLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = XmlLink
        fields = ['id', 'xml_link', 'rss_type']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'title', 'description', 'last_update', 'language', 'subtitle',
                  'image', 'author', 'xml_link', 'category', 'owner']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class BaseItemSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'title', 'channel', 'liked', 'bookmarked', 'guid', 'pub_date', 'image']




class PodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podcast
        fields = ['id', 'title', 'channel', 'guid', 'pub_date', 'image',
                  'subtitle', 'description', 'audio_file', 'explicit']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'channel', 'guid', 'pub_date', 'image',
                  'source', 'link']
        extra_kwargs = {
            'id': {'read_only': True}
        }