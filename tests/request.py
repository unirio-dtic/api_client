# coding=utf-8
import random
import unittest
from unirio.api import UNIRIOAPIRequest
from unirio.api.exceptions import *
from tests import config
try:
    from string import lowercase
except ImportError:
    # Python 3.x
    from string import ascii_lowercase as lowercase


class TestAPIRequest(unittest.TestCase):
    API_KEY_VALID = "1a404993f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07fdfbe0587c6ef14e5c92"
    API_KEY_INVALID = "INVALIDA93f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07f0587c6ef14e5c93"

    valid_endpoint = 'UNIT_TEST'
    valid_endpoint_pkey = 'ID_UNIT_TEST'

    endpoints = {
        'invalid_permission': ('PROJETOS', 'ALUNOS', 'PESSOAS',),
        'invalid_endpoints': ('fbsdfgsdfg', 'grgsuer9gsfh8sdfh', 'daba4a0as0haf')
    }

    CLOB_FIELD = 'CLOBCOL'

    @property
    def _operador_mock(self):
        # todo Para fins de teste, é relevante que COD_OPERADOR seja de tipo compativel com a realidade das tabelas?
        return {'COD_OPERADOR': self._random_string(3)}

    def setUp(self):
        global env
        self.api = UNIRIOAPIRequest(self.API_KEY_VALID, config.ENV, cache=None, debug=True)

    def _random_string(self, length):
        return ''.join(random.choice(lowercase) for i in range(length))

    def _invalid_dummy_params(self):
        params = {'INVALID_FIELD_%s' % self._random_string(3): random.randint(100, 10000)}
        params.update(self._operador_mock)
        return params


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
