import re
from xml.etree import ElementTree


class XmlTrimmer:

    def __init__(self, trimming_config, whitelisted_attributes):
        self.trimming_config = trimming_config
        whitelisted_attributes = whitelisted_attributes if whitelisted_attributes else {}
        self.whitelisted_attributes = whitelisted_attributes

    @staticmethod
    def remove_namespaces(element: ElementTree.Element):
        element.tag = re.sub(r'{.*}', '', element.tag)
        for child in element:
            XmlTrimmer.remove_namespaces(child)

    @staticmethod
    def remove_namespace(string):
        return re.sub('{.*}', '', string)

    def trim(self, element, trim_config=None):
        if trim_config is None:
            trim_config = self.trimming_config

        for child in element:
            tag = self.remove_namespace(child.tag)
            if tag in trim_config:
                config = trim_config[tag]
                if type(config) == str:
                    self.remove_by_config(element, child, config)
                else:
                    self.trim(child, config)

    def remove_by_config(self, parent, child, config):
        if config == 'self':
            parent.remove(child)
        else:
            regex = config
            self.remove_children(child, regex)

    def remove_children(self, element, pattern):
        for child in element:
            tag = self.remove_namespace(child.tag)
            if re.match(pattern, tag) and not self.is_whitelisted(child):
                element.remove(child)

    def is_whitelisted(self, element):
        common_attributes = set(element.keys()).intersection(self.whitelisted_attributes.keys())
        return any(element.get(attrib) in self.whitelisted_attributes.get(attrib) for attrib in common_attributes)