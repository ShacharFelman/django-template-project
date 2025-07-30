from django.test import TestCase
from rest_framework.test import APITestCase
import logging


class ExampleOfBaseTestCase(TestCase):
    """Example of base test case with logging suppression for clean test output."""
    
    def setUp(self):
        super().setUp()
        # Suppress common loggers during tests
        logging.getLogger('example').setLevel(logging.CRITICAL)
        logging.getLogger('core').setLevel(logging.CRITICAL)


class ExampleOfBaseAPITestCase(APITestCase):
    """Example of base API test case with logging suppression for clean test output."""
    
    def setUp(self):
        super().setUp()
        # Suppress common loggers during tests
        logging.getLogger('example').setLevel(logging.CRITICAL)
        logging.getLogger('core').setLevel(logging.CRITICAL) 