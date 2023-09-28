from rssfeeds.models import Channel, Podcast, News
from .models import Recommendation


def get_item_model(channel):
    return Podcast if (hasattr(channel, 'podcast_set') and len(channel.podcast_set.all()) > 0) else News


def update_recommendations(user, categories, increment_count=1):
    for category in categories:
        recommend_obj, created = Recommendation.objects.get_or_create(user=user, category=category)
        recommend_obj.count += increment_count
        recommend_obj.save()