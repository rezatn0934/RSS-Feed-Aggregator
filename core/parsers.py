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

    def get_categories(self, element, parent=None, parent_list=None):
        """
        Get a hierarchical structure of <itunes:category> elements within an element.

        Args:
            element (Element): The parent element.
            parent (Category or None): The parent category.
            :param element:
            :param parent:
            :param parent_list:
        Returns:
            Category: A hierarchical structure of categories.
        """
        if parent_list is None:
            parent_list = []
        tag = 'itunes:category'
        category_elements = element.findall(tag, namespaces=self.itunes_namespace)
        for category_element in category_elements:
            name = category_element.attrib.get("text")
            child_category = CategoryNode(name, parent)
            parent_list.append(child_category)
            if category_element.findall(tag, namespaces=self.itunes_namespace):
                self.get_categories(category_element, child_category)

        return parent_list

    def get_element_text(self, element, tag):
        """
        Get the text content of a sub-element within an element.

        Args:
            element (Element): The parent element.
            tag (str): The tag name of the sub-element.

        Returns:
            str: The text content of the sub-element, or an empty string if not found.
        """
        sub_element = element.find(tag, namespaces=self.itunes_namespace)
        return sub_element.text if sub_element is not None else ''

