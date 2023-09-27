from rest_framework.response import Response
from rest_framework import status

from rssfeeds.models import Channel
from .utils import get_item_model, update_recommendations


class InteractionMixin:

  