import unittest
from unittest.mock import patch
import os
import sys
import json
from jsonschema import validate


class TestFrankandoakImportProductsTransformers(unittest.TestCase):
    @staticmethod
    def _assert_json(test_case, json1, json2):
        if isinstance(json1, dict):
            if sys.version_info >= (3, 0):
                for key, value in json1.items():
                    TestFrankandoakImportProductsTransformers._assert_json(test_case, value, json2[key])
            else:
                for key, value in json1.iteritems():
                    TestFrankandoakImportProductsTransformers._assert_json(test_case, value, json2[key])
        elif isinstance(json1, list):
            for i, value in enumerate(json1):
                TestFrankandoakImportProductsTransformers._assert_json(test_case, value, json2[i])
        else:
            test_case.assertEqual(json1, json2)

    @staticmethod
    def _load_json_file(filename):
        filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures', filename)
        with open(filepath) as json_content:
            return json.load(json_content)

    @staticmethod
    def _load_jsonl_file(filename):
        filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures', filename)
        with open(filepath) as jsonl_content:
            return jsonl_content.read()

    def setUp(self):
        self.variables = {
            'url_image_placeholder': 'url_image_placeholder'
        }
        self.os_env = patch.dict('os.environ', self.variables)
        self.os_env.start()

        param_store_mock = patch('shopify_import_products.shopify.param_store_config.ParamStoreConfig')
        self.patched_param_store_mock = param_store_mock.start()
        self.patched_param_store_mock.get_shopify_config.return_value = {
            "shop": "shop",
            "username": "username",
            "password": "password"
        }
        from shopify_import_products.transformers import transform # pylint: disable=C0415
        self.transform = transform

    def test_transform(self):
        products_jsonl = self._load_jsonl_file('shopify_products.jsonl')
        products_transformed = self._load_json_file('products_transformed.json')
        categories_transformed = self._load_json_file('categories_transformed.json')

        products, categories = self.transform.transform_products(products_jsonl)

        self._assert_json(self, products, products_transformed)
        self._assert_json(self, products_transformed, products)
        self._assert_json(self, categories, categories_transformed)
        self._assert_json(self, categories_transformed, categories)

        prod_schema = self._load_json_file('products_schema.json')
        cat_schema = self._load_json_file('categories_schema.json')

        try:
            validate(products, prod_schema)
            validate(categories, cat_schema)
        except Exception as ex:
            raise self.failureException('{} raised'.format(ex))

    def test_transform_fr(self):
        products_jsonl = self._load_jsonl_file('shopify_products.jsonl')
        products_transformed = self._load_json_file('products_transformed_fr.json')
        categories_transformed = self._load_json_file('categories_transformed_fr.json')

        products, categories = self.transform.transform_products(products_jsonl, 'fr-CA')

        self._assert_json(self, products, products_transformed)
        self._assert_json(self, products_transformed, products)
        self._assert_json(self, categories, categories_transformed)
        self._assert_json(self, categories_transformed, categories)

        prod_schema = self._load_json_file('products_schema.json')
        cat_schema = self._load_json_file('categories_schema.json')

        try:
            validate(products, prod_schema)
            validate(categories, cat_schema)
        except Exception as ex:
            raise self.failureException('{} raised'.format(ex))