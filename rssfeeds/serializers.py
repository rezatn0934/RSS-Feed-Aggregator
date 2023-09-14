from rest_framework import serializers

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