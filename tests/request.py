import unittest
from unirio.api import UNIRIOAPIRequest, APIServer, APIResultObject
from unirio.api.exceptions import *


class TestGetRequest(unittest.TestCase):
    API_KEY_VALID = "632c5fa0d71e727b1326792bced2dc4aef85a250f9555ed36c3e07f60df4cdbe53b8659c7717bab1606630d663654fd7"
    API_KEY_INVALID = "ffd8eb0ac0e5725c03dc458c1589b2fd2a734859fe7e9d1d9e74952b119efc6a23f3173965bf8a9ccc09475fa0571624"

    endpoints = {
        'valid': ('PESSOAS', 'ALUNOS',),
        'invalid_permission': ('PROJETOS',),
        'invalid_endpoints': ('fbsdfgsdfg', 'grgsuer9gsfh8sdfh', 'daba4a0as0haf')
    }

    def setUp(self):
        self.api = UNIRIOAPIRequest(self.API_KEY_VALID, APIServer.PRODUCTION, cache=None)

    def test_valid_endpoint_with_permission(self):
        for path in self.endpoints['valid']:
            result = self.api.get(path)
            self.assertIsInstance(result, APIResultObject)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.get(path)

    def test_invalid_endpoint(self):
        for path in self.endpoints['invalid_endpoints']:
            with self.assertRaises(InvalidEndpointException):
                self.api.get(path)

