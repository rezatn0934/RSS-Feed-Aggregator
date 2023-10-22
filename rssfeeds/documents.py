from django_elasticsearch_dsl.documents import DocType

from .models import Channel, Podcast, News

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry


@registry.register_document
class ChannelDocument(Document):

    title = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',
    )
    id = fields.IntegerField(attr='id')

    description = fields.TextField()
    last_update = fields.DateField()
    language = fields.KeywordField()
    subtitle = fields.TextField()
    image = fields.KeywordField()
    author = fields.TextField()
    xml_link = fields.ObjectField(properties={
        'xml_link': fields.KeywordField(),
        'rss_type': fields.ObjectField(properties={
            'name': fields.KeywordField(),
        })
    })
    category = fields.ObjectField(properties={
        'name': fields.KeywordField(),
    })
    owner = fields.KeywordField()

    class Django:
        model = Channel

