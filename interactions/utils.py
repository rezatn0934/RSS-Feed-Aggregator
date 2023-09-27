from rssfeeds.models import Channel, Podcast, News
from .models import Recommendation


def get_item_model(channel):
    return Podcast if hasattr(channel, 'podcast_set') else News
