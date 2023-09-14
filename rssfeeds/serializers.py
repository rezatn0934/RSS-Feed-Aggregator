from rest_framework import serializers

from .models import XmlLink


class XmlLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = XmlLink
        fields = ['xml_link', 'rss_type']
