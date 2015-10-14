import random
import unittest
from unirio.api import UNIRIOAPIRequest, APIServer
from unirio.api.exceptions import *
from unirio.api.result import *
import warnings
import string

env = APIServer.LOCAL


class TestAPIRequest(unittest.TestCase):
    API_KEY_VALID = "1a404993f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07fdfbe0587c6ef14e5c92"
    API_KEY_INVALID = "INVALIDA93f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07f0587c6ef14e5c93"

    valid_endpoint = 'UNIT_TEST'
    valid_endpoint_pkey = 'ID_UNIT_TEST'

    endpoints = {
        'invalid_permission': ('PROJETOS', 'ALUNOS', 'PESSOAS',),
        'invalid_endpoints': ('fbsdfgsdfg', 'grgsuer9gsfh8sdfh', 'daba4a0as0haf')
    }

    def setUp(self):
        global env
        self.api = UNIRIOAPIRequest(self.API_KEY_VALID, env, cache=None)

    def _random_string(self, length):
        return ''.join(random.choice(string.lowercase) for i in xrange(length))

    def _invalid_dummy_params(self):
        return {'INVALID_FIELD_%s' % self._random_string(3): random.randint(100, 10000)}


class TestAPIKey(TestAPIRequest):
    def test_valid_key(self):
        try:
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
                self.assertTrue(i[field] <= j[field])

    def test_valid_endpoint_with_permission_and_invalid_parameters(self):
        result = self.api.get(
            self.valid_endpoint,
            {self._random_string(3): self._random_string(3) for i in xrange(0, 4)}
        )
        self.assertIsInstance(result, APIResultObject)

    def test_valid_endpoint_with_permission_and_invalid_empty_parameters_value(self):
        result = self.api.get(
            self.valid_endpoint,
            {self._random_string(3): '' for i in xrange(0, 4)}
        )
        self.assertIsInstance(result, APIResultObject)

    def test_valid_endpoint_with_permission_and_list_parameters_types(self):
        result = self.api.get(
            self.valid_endpoint,
            {'PROJNAME': tuple(self._random_string(i) for i in xrange(0, 10))}
        )
        self.assertIsInstance(result, APIResultObject)



class TestPOSTRequest(TestAPIRequest):
    not_null_keys = ('PROJNO', 'PROJNAME', 'DEPTNO', 'RESPEMP', 'MAJPROJ',)


    @property
    def valid_entry(self):
        return {k: self._random_string(3) for k in self.not_null_keys}

    def test_valid_endpoint_with_permission(self):
        new_resource = self.api.post(self.valid_endpoint, self.valid_entry)
        self.assertIsInstance(new_resource, APIPOSTResponse)

    def test_valid_endpoint_with_permission_and_empty_arguments(self):
        with self.assertRaises(InvalidParametersException):
            self.api.post(self.valid_endpoint, {})

    def test_valid_endpoint_with_permision_and_invalid_arguments(self):
        with self.assertRaises(InvalidParametersException):
            entry = {k: random.randint(1000, 10000) for k in self.not_null_keys}
            self.api.post(self.valid_endpoint, entry)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.post(path, {})

    def test_endpoint_blob(self):
        pass

    def test_endpoint_clob(self):
        entry = self.valid_entry
        entry.update(
            {'CLOBCOL': self._random_string(10000)}
        )
        new_resource = self.api.post(self.valid_endpoint, entry)

        self.assertIsInstance(new_resource, APIPOSTResponse)


class TestPUTRequest(TestAPIRequest):
    @property
    def __valid_entry(self):
        """
        :rtype : dict
        """
        return self.api.get(self.valid_endpoint).content[0]

    def test_valid_endpoint_without_primary_key(self):
        PROJNAME = self._random_string(3)
        with self.assertRaises(MissingPrimaryKeyException):
            result = self.api.put(self.valid_endpoint, {'PROJNAME': PROJNAME})

    def test_valid_endpoint_with_permission(self):
        PROJNAME = self._random_string(3)
        result = self.api.put(self.valid_endpoint, {
            self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey],
            'PROJNAME': PROJNAME
        })
        self.assertIsInstance(result, APIPUTResponse)

        updated_entry = self.api.get(
            self.valid_endpoint,
            {self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey]}
        ).first()
        self.assertEqual(updated_entry['PROJNAME'], PROJNAME)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.put(path, {'INVALID_FIELD_CVCBSDG': 'An invalid data'})

    def test_valid_endpoint_with_valid_permission_and_invalid_parameters_types(self):
        entry = self.__valid_entry
        entry.update({'PROJNAME': 235235})
        with self.assertRaises(InvalidParametersException):
            self.api.put(self.valid_endpoint, entry)


class TestDELETERequest(TestAPIRequest):
    BIG_FAKE_ID = 2749873460397

    @property
    def __dummy_ids(self):
        ids = {
            'PROJETOS': {'ID_PROJETO': 100},
            'PESSOAS': {'ID_PESSOA': 100},
            'ALUNOS': {'ID_ALUNO': 100},
        }
        return ids

    @property
    def __valid_entry(self):
        """
        :rtype : dict
        """
        return self.api.get(self.valid_endpoint).content[0]

    def test_valid_endpoint_with_permission(self):
        result = self.api.delete(
            self.valid_endpoint,
            {self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey]}
        )
        self.assertTrue(result.affectedRows >= 1)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.delete(path, self.__dummy_ids[path])

    def test_invalid_endpoint(self):
        for path in self.endpoints['invalid_endpoints']:
            with self.assertRaises(ContentNotFoundException):
                self.api.delete(path, {})
                self.api.delete(path, self._invalid_dummy_params())

    def test_valid_endpoint_without_pkey(self):
        with self.assertRaises(MissingPrimaryKeyException):
            self.api.delete(self.valid_endpoint, self._invalid_dummy_params())

    def test_invalid_entry(self):
        with self.assertRaises(NothingToUpdateException):
            self.api.delete(self.valid_endpoint, {self.valid_endpoint_pkey: self.BIG_FAKE_ID})
