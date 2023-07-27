import copy
from enum import IntEnum
from typing import Type, Union, TypeVar, _GenericAlias, Any, List
from dataclasses import fields, dataclass, is_dataclass
from xml.etree import ElementTree
from newstore_common.sfcc.xml_api.order.common_fields import TextNode

dc_type = TypeVar('DataClass')


class NamingConvention(IntEnum):
    DEFAULT = 0
    SNAKE_CASE = 1
    LOWER_CAMEL_CASE = 2
    UPPER_CAMEL_CASE = 3
    KEBAB_CASE = 4


class XmlMarshaller:

    def __init__(
            self,
            source_casing: NamingConvention,
            data_class_field_casing: NamingConvention = NamingConvention.SNAKE_CASE,
            has_wrapper_around_lists: bool = False):
        self.has_wrapper_around_lists = has_wrapper_around_lists
        self._source_casing = source_casing
        self._data_class_field_casing = data_class_field_casing

    def xml_to_dataclass(self, xml_element: ElementTree.Element, data_class: dc_type) -> dc_type:
        element_copy = copy.deepcopy(xml_element)
        self._map_element_casing(element_copy)
        return self._build_dataclass(element_copy, data_class)

    def _map_element_casing(self, xml_element: ElementTree.Element):
        tokens = self._split_to_tokens(xml_element.tag)
        xml_element.tag = self._combine_tokens(tokens)
        for child in xml_element:
            self._map_element_casing(child)

    def _split_to_tokens(self, tag: str) -> List[str]:
        if self._source_casing == NamingConvention.KEBAB_CASE:
            return tag.split('-')
        elif self._source_casing == NamingConvention.SNAKE_CASE:
            return tag.split('_')
        else:
            raise Exception(f'Source case not supported yet {self._source_casing.name}')

    def _combine_tokens(self, tokens: List[str]) -> str:
        if self._data_class_field_casing == NamingConvention.SNAKE_CASE:
            return '_'.join(tokens)
        elif self._data_class_field_casing == NamingConvention.KEBAB_CASE:
            raise Exception(f'Destination case is not a valid python naming convention '
                            f'{self._data_class_field_casing.name}')
        else:
            raise Exception(f'Destination case not supported yet '
                            f'{self._data_class_field_casing.name}')

    def _build_dataclass(
            self,
            xml_element: ElementTree.Element,
            data_class: dataclass,
            outer_type: Type = None) -> dataclass:
        if not xml_element:
            if outer_type is None:
                outer_type = data_class
            return self._create_from_leaf_element(xml_element, outer_type)

        dataclass_params = {}

        for field in fields(data_class):
            elements = xml_element.findall(field.name)
            if self._is_list_type(field.type):
                if self.has_wrapper_around_lists and elements:
                    parent = next(el for el in elements)
                    elements = (el for el in parent)
                inner_type = self._get_inner_type(field.type)
                dataclass_params[field.name] = [self._build_dataclass(el, inner_type, inner_type)
                                                for el in elements]
            elif self._is_optional_type(field.type):
                inner_type = self._get_inner_type(field.type)
                child = elements[0] if elements else None
                dataclass_params[field.name] = self._build_dataclass(child, inner_type, field.type)
            elif not elements:
                dataclass_params[field.name] = None
            else:
                dataclass_params[field.name] = self._build_dataclass(
                    elements[0], field.type, field.type)

        if 'attributes' in map(lambda f: f.name, fields(data_class)):
            dataclass_params['attributes'] = xml_element.attrib

        return data_class(**dataclass_params)

    def _create_from_leaf_element(
            self,
            xml_element: ElementTree.Element,
            field_type: Union[type, _GenericAlias]) -> Any:
        if field_type == bool:
            return xml_element.text.lower() in ['true', '1']
        elif field_type == TextNode:
            return TextNode(attributes=xml_element.attrib,
                            text=xml_element.text)
        elif self._is_optional_type(field_type):
            if xml_element is None or xml_element.text is None:
                return None
            else:
                constructor = self._get_inner_type(field_type)
                return constructor(xml_element.text)
        elif not is_dataclass(field_type):
            return field_type(xml_element.text)
        else:
            return None

    def _get_inner_type(self, field_type) -> Type:
        return field_type.__args__[0]

    def _is_list_type(self, type_: Type) -> bool:
        try:
            return type_.__origin__ == list
        except AttributeError:
            return False

    def _is_optional_type(self, type_: Type) -> bool:
        return self._is_union(type_) and type(None) in type_.__args__

    def _is_union(self, type_: Type) -> bool:
        return self._is_generic(type_) and type_.__origin__ == Union

    def _is_generic(self, type_: Type) -> bool:
        return hasattr(type_, '__origin__')


