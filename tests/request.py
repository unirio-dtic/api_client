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
        return {'COD_OPERADOR': random.randint(10, 1000)}

    def mock_blob(self):
        """
        :return: Uma string correspondente ao conteudo de um arquivo em seu formato b64
        """
        from base64 import b64encode

        with open(__file__, 'r') as f:
            file_content = f.read()
            try:
                return b64encode(file_content)
            except TypeError:
                # Python 3.x
                return b64encode(bytes(file_content, encoding='utf-8')).decode('utf-8')

    def setUp(self):
        self.api = UNIRIOAPIRequest(config.KEY, config.SERVER, cache=None, debug=False)

    @staticmethod
    def random_string(length):
        return ''.join(random.choice(lowercase) for i in range(length))

    def _invalid_dummy_params(self):
        params = {'INVALID_FIELD_%s' % self.random_string(3): random.randint(100, 10000)}
        params.update(self._operador_mock)
        return params

    def _convert_entry_keys_case(self, case, entry):
        return {getattr(k, case)(): v for k, v in entry.items()}


class TestAPIKey(TestAPIRequest):
    def test_valid_key(self):
        try:
            self.api.get(self.valid_endpoint)
        except InvalidAPIKeyException:
            self.fail("test_valid_key() failed. A valid key is being invalidated.")

    def test_invalid_key(self):
        self.api.api_key = config.Keys['INVALID']
        with self.assertRaises(InvalidAPIKeyException):
            self.api.get(self.valid_endpoint)
