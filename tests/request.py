import unittest
from unirio.api import UNIRIOAPIRequest, APIServer, APIResultObject
from unirio.api.exceptions import *
from datetime import datetime
from unirio.api.result import APIPOSTResponse
import warnings


class TestAPIRequest(unittest.TestCase):
    API_KEY_VALID = "1a404993f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07fdfbe0587c6ef14e5c92"
    API_KEY_INVALID = "INVALIDA93f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07f0587c6ef14e5c93"

    valid_endpoint = 'UNIT_TEST'
    endpoints = {
        'invalid_permission': ('PROJETOS', 'ALUNOS', 'PESSOAS',),
        'invalid_endpoints': ('fbsdfgsdfg', 'grgsuer9gsfh8sdfh', 'daba4a0as0haf')
    }

    def setUp(self):
        self.api = UNIRIOAPIRequest(self.API_KEY_VALID, APIServer.PRODUCTION_DEVELOPMENT, cache=None)


class TestAPIKey(TestAPIRequest):
    def test_valid_key(self):
        try:
            with self.assertRaises(NoContentException):
                self.api.get(self.valid_endpoint)
        except InvalidAPIKeyException:
            self.fail("test_valid_key() failed. A valid key is being invalidated.")

    def test_invalid_key(self):
        self.api.api_key = self.API_KEY_INVALID
        with self.assertRaises(InvalidAPIKeyException):
            self.api.get(self.valid_endpoint)


class TestGETRequest(TestAPIRequest):
    def test_valid_endpoint_with_permission(self):
        try:
            result = self.api.get(self.valid_endpoint)
            self.assertIsInstance(result, APIResultObject)
        except NoContentException:
            warnings.warn("Test passed but should be run again with content on test endpoint %s" % self.valid_endpoint)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.get(path)

    def test_invalid_endpoint(self):
        for path in self.endpoints['invalid_endpoints']:
            with self.assertRaises(InvalidEndpointException):
                self.api.get(path)

    def test_orderby(self):
        fields = ('PROJNAME', 'DEPTNO',)
        for field in fields:
            result = self.api.get(self.valid_endpoint, {'ORDERBY': field})
            for i, j in zip(result.content, result.content[1:]):
                self.assertTrue(i[field] < j[field])


class TestPOSTRequest(TestAPIRequest):
    not_null_keys = ('PROJNO', 'PROJNAME', 'DEPTNO', 'RESPEMP', 'MAJPROJ',)
    primary_key = 'ID_UNIT_TEST'

    def test_valid_endpoint_with_permission(self):
        valid_entry = {k: 'abc' for k in self.not_null_keys}
        new_resource = self.api.post(self.valid_endpoint, valid_entry)
        self.assertIsInstance(new_resource, APIPOSTResponse)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ContentNotCreatedException):
                new_resource = self.api.post(path, {})

    def test_endpoint_blob(self):
        pass

    def test_endpoint_clob(self):
        pass