from django_elasticsearch_dsl.documents import DocType
from elasticsearch_dsl import analyzer

from .models import Channel, Podcast, News

from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry


class BaseDocument(DocType):

    class Index:
        name = None
        settings = {
            'number_of_shards': 5,
            'number_of_replicas': 1,
        }

    id = fields.IntegerField(attr='id')
    title = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',
    )
    channel = fields.ObjectField(properties={
        'title': fields.TextField(fields={'raw': fields.KeywordField()},
                                  analyzer='standard', ),
        'last_update': fields.DateField(),
    })
    pub_date = fields.DateField()

    class Django:
        model = None

    def get_queryset(self):
        return super().get_queryset().select_related('channel')

    def prepare_channel(self, instance):
        return {'title': instance.channel.title, 'last_update': instance.channel.last_update}


@registry.register_document
class ChannelDocument(Document):
    class Index:
        name = 'channel_index'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    title = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',
    )
    id = fields.IntegerField(attr='id')

    description = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',
    )

    last_update = fields.DateField()
    language = fields.KeywordField()
    subtitle = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',)
    image = fields.KeywordField()
    author = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',)
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

    def get_queryset(self):
        return super().get_queryset().prefetch_related('xml_link__rss_type', 'category')

    def prepare_category(self, instance):
        category_names = [category.name for category in instance.category.all()]
        return {
            'name': category_names,
        }
    def prepare_xml_link(self, instance):
        return {
            'xml_link': instance.xml_link.xml_link,
            'rss_type': {
                'name': instance.xml_link.rss_type.name,
            },
        }


@registry.register_document
class PodcastDocument(BaseDocument):
    class Index(BaseDocument.Index):
        name = 'podcast_index'

    subtitle = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard',
    )
    description = fields.TextField(
        fields={'raw': fields.KeywordField()},
        analyzer='standard', )
    duration = fields.KeywordField()
    audio_file = fields.KeywordField()
    explicit = fields.BooleanField()

    class Django:
        model = Podcast


@registry.register_document
class NewsDocument(BaseDocument):
    class Index(BaseDocument.Index):
        name = 'news_index'

    source = fields.KeywordField()
    link = fields.KeywordField()

    class Django:
        model = News
