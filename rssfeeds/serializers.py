
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
    subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = ['id', 'title', 'description', 'last_update', 'language', 'subtitle',
                  'image', 'author', 'xml_link', 'category', 'owner']
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def get_subscribed(self, obj):
        user = self.context['request'].user
        return Like.objects.filter(
            id=obj.pk,
            user=user
        ).exists()

class BaseItemSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'title', 'channel', 'liked', 'bookmarked', 'guid', 'pub_date', 'image']

    def get_liked(self, obj):
        user = self.context['request'].user
        content_type = ContentType.objects.get_for_model(obj)
        return Like.objects.filter(
            object_id=obj.pk,
            content_type=content_type,
            user=user
        ).exists()

    def get_bookmarked(self, obj):
        user = self.context['request'].user
        content_type = ContentType.objects.get_for_model(obj)
        return BookMark.objects.filter(
            object_id=obj.pk, content_type=content_type, user=user).exists()


class PodcastSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        model = Podcast
        fields = BaseItemSerializer.Meta.fields + ['subtitle', 'description', 'audio_file', 'explicit']


class NewsSerializer(BaseItemSerializer):
    class Meta(BaseItemSerializer.Meta):
        model = News
        fields = BaseItemSerializer.Meta.fields + ['source', 'link']
