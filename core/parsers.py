import xml.etree.ElementTree as ET
from datetime import datetime
from abc import ABC, abstractmethod
from category_node import CategoryNode

import requests


class Parser(ABC):
    """
    Abstract base class for parsing XML data and creating records from it.

    Attributes:
        itunes_namespace (dict): Namespace for iTunes elements.
        root (Element): The root element of the XML data.
        channel_data (Element): The channel element within the XML data.

    Methods:
        item_parser(item): Abstract method to parse individual items within the XML.
        parse_xml_and_create_records(): Abstract method to parse the entire XML and create records.
        get_element_text(element, tag): Get the text content of a sub-element within an element.
        get_element_attr(element, tag, attr): Get the attribute value of a sub-element within an element.
        parse_date(date_str): Parse a date string into a datetime object.
        parse_channel(): Parse the channel data from the XML.
    """

    def __init__(self, xml_data):
        """
        Initialize the Parser with XML data.

        Args:
            xml_data (str): The XML data to parse.
        """
        self.itunes_namespace = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        self.atom_namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        self.googleplay_namespace = {'googleplay': 'http://www.google.com/schemas/play-podcasts/1.0'}
        self.media_namespace = {'media': 'http://search.yahoo.com/mrss/'}
        self.content_namespace = {'content': 'http://purl.org/rss/1.0/modules/content/'}
        self.root = ET.fromstring(xml_data)
        self.channel_data = self.root.find('channel')

    @abstractmethod
    def item_parser(self, item):
        """
        Abstract method to parse individual items within the XML.

        Args:
            item (Element): The XML element representing an item.

        Returns:
            dict: Parsed data from the item.
        """
        pass

    @abstractmethod
    def parse_xml_and_create_records(self):
        """
        Abstract method to parse the entire XML and create records.

        Returns:
            dict: Parsed data from the channel and items.
        """
        pass
