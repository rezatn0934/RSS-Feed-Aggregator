from core.parsers import PodcastParser, NewsParser
from core.models import Category
from .models import Podcast, News
import requests


def parse_podcast_data(xml_link):
    response = requests.get(xml_link.xml_link)
    [Parser, model] = item_model_mapper(xml_link.rss_type.name)
    return [Parser(response.text).parse_xml_and_create_records(), model]
