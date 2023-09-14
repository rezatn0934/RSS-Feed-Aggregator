from core.parsers import PodcastParser, NewsParser
from core.models import Category
from .models import Podcast, News
import requests


def parse_podcast_data(xml_link):
    response = requests.get(xml_link.xml_link)
    [Parser, model] = item_model_mapper(xml_link.rss_type.name)
    return [Parser(response.text).parse_xml_and_create_records(), model]


def item_model_mapper(arg):
    choice = {
        "Podcast": [PodcastParser, Podcast],
        "News": [NewsParser, News],
    }
    return choice[arg.capitalize()]


def create_or_update_categories(categories_data):
    categories = []
    for category_data in categories_data:
        parent, _ = Category.objects.get_or_create(name=category_data.name)
        categories.append(parent)
        for child_data in category_data.children:
            child, _ = Category.objects.get_or_create(name=child_data.name, parent=parent)
            categories.append(child)
    return categories
