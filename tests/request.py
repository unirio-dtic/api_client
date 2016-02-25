# coding=utf-8
import random
import unittest
import warnings
from collections import Iterable, Sized

from datetime import timedelta, date

from unirio.api import UNIRIOAPIRequest, APIServer
from unirio.api.exceptions import *
from unirio.api.result import *
try:
    from string import lowercase
except ImportError:
    # Python 3.x
    from string import ascii_lowercase as lowercase

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

    CLOB_FIELD = 'CLOBCOL'

    @property
    def _operador_mock(self):
        # todo Para fins de teste, é relevante que COD_OPERADOR seja de tipo compativel com a realidade das tabelas?
        return {'COD_OPERADOR': self._random_string(3)}

    def setUp(self):
        global env
        self.api = UNIRIOAPIRequest(self.API_KEY_VALID, env, cache=None, debug=True)

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


class TestGETRequest(TestAPIRequest):
    def test_valid_endpoint_with_permission(self):
        try:
            result = self.api.get(self.valid_endpoint)
            self.assertIsInstance(result, APIResultObject)
        except NoContentException:
            self.__no_content_warning()

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.get(path)

    def test_invalid_endpoint(self):
        for path in self.endpoints['invalid_endpoints']:
            with self.assertRaises(InvalidEndpointException):
                self.api.get(path)

    def __test_orderby(self, params, assertion):
        fields = ('PROJNAME', 'DEPTNO',)
        for field in fields:
            p = params.copy()
            p.update({'ORDERBY': field})
            result = self.api.get(self.valid_endpoint, p)
            not_null_entries = [entry for entry in result.content if entry[field]]
            for i, j in zip(not_null_entries, not_null_entries[1:]):
                assertion(i[field], j[field])

    def test_orderby_asc_without_sort(self):
        self.__test_orderby({}, self.assertLessEqual)

    def test_orderby_asc_with_sort(self):
        self.__test_orderby({'SORT': 'ASC'}, self.assertLessEqual)

    def test_orderby_desc(self):
        self.__test_orderby({'SORT': 'DESC'}, self.assertGreaterEqual)

    def test_orderby_invalid_field(self):
        with self.assertRaises(InvalidParametersException):
            self.api.get(self.valid_endpoint, {'ORDERBY': self._random_string(10)})

    def test_orderby_with_invalid_sort(self):
        with self.assertRaises(InvalidParametersException):
            self.__test_orderby({'SORT': self._random_string(6)}, None)

    def test_valid_endpoint_with_permission_and_invalid_parameters(self):
        with self.assertRaises(InvalidParametersException):
            self.api.get(
                self.valid_endpoint,
                {self._random_string(3): self._random_string(3) for i in range(0, 4)}
            )

    def test_valid_endpoint_with_permission_and_invalid_empty_parameters_value(self):
        with self.assertRaises(NullParameterException):
            result = self.api.get(
                self.valid_endpoint,
                {self._random_string(3): '' for i in range(0, 4)}
            )
            self.assertIsInstance(result, APIResultObject)

    def test_valid_endpoint_with_permission_and_invalid_list_parameters_types(self):
        with self.assertRaises(NoContentException):
            self.api.get(
                self.valid_endpoint,
                {'PROJNAME_SET': tuple(self._random_string(i) for i in range(0, 10))}
            )

    def test_valid_endpoint_with_permission_and_valid_list_parameters_types(self):
        entries = tuple(entry['PROJNAME'] for entry in self.api.get(self.valid_endpoint).content if entry['PROJNAME'])
        result = self.api.get(self.valid_endpoint, {'PROJNAME_SET': entries}).content
        self.assertEqual(set(entries), set([i['PROJNAME'] for i in result]))

    def test_first_valid_content(self):
        try:
            result = self.api.get(self.valid_endpoint).first()
            self.assertIsInstance(result, dict)
        except NoContentException:
            self.__no_content_warning()

    def test_first_invalid_params(self):
        for path in self.endpoints['invalid_permission'] + self.endpoints['invalid_endpoints']:
            with self.assertRaises(APIException):
                self.api.get(path).first()

    def __no_content_warning(self):
        warnings.warn("Test passed but should be run again with content on test endpoint %s" % self.valid_endpoint)

    def test_valid_endpoint_with_content_bypassing_no_content_exception(self):
        l = self.api.get(self.valid_endpoint, bypass_no_content_exception=True)
        self.assertIsInstance(l, Iterable)

    def test_valid_endpoint_without_content_bypassing_no_content_exception(self):
        l = self.api.get(
            self.valid_endpoint,
            {self.valid_endpoint_pkey: 99999999999999999999999999999},
            bypass_no_content_exception=True
        )
        self.assertIsInstance(l, Iterable)
        self.assertIsInstance(l, Sized)
        self.assertEqual(len(l), 0)

    def test_get_invalid_endpoint_bypassing_no_content_exception(self):
        with self.assertRaises(InvalidEndpointException):
            self.api.get(self.endpoints['invalid_endpoints'][0], bypass_no_content_exception=True)

    def test_get_single_result_with_content(self):
        single_result = self.api.get_single_result(self.valid_endpoint)
        self.assertIsInstance(single_result, dict)

    def test_get_single_result_without_content(self):
        with self.assertRaises(NoContentException):
            self.api.get_single_result(self.valid_endpoint, {self.valid_endpoint_pkey: 99999999999999999999999999999})

    def test_get_single_result_invalid_endpoint(self):
        with self.assertRaises(InvalidEndpointException):
            self.api.get_single_result(self.endpoints['invalid_endpoints'][0])

    def test_get_single_result_with_content_bypassing_no_content_exception(self):
        single_result = self.api.get_single_result(self.valid_endpoint, bypass_no_content_exception=True)
        self.assertIsInstance(single_result, dict)

    def test_get_single_result_without_content_bypassing_no_content_exception(self):
        single_result = self.api.get_single_result(self.valid_endpoint,
                                                   {self.valid_endpoint_pkey: 99999999999999999999999999999},
                                                   bypass_no_content_exception=True)
        self.assertEquals(single_result, None)

    def test_get_single_result_invalid_endpoint_bypassing_no_content_exception(self):
        with self.assertRaises(InvalidEndpointException):
            self.api.get_single_result(self.endpoints['invalid_endpoints'][0], bypass_no_content_exception=True)


class TestPOSTRequest(TestAPIRequest):
    not_null_keys = ('PROJNO', 'PROJNAME', 'DEPTNO', 'RESPEMP', 'MAJPROJ', 'COD_OPERADOR')

    @property
    def valid_entry(self):
        return {k: self._random_string(3) for k in self.not_null_keys}

    def test_valid_endpoint_with_permission(self):
        new_resource = self.api.post(self.valid_endpoint, self.valid_entry)
        self.assertIsInstance(new_resource, APIPOSTResponse)

    def test_valid_endpoint_with_permission_and_empty_arguments(self):
        try:
            result = self.api.post(self.valid_endpoint, self._operador_mock)
        except APIException as e:
            self.assertIsInstance(e, InvalidParametersException)
        else:
            self.assertIsInstance(result, APIPOSTResponse,
                                  "Tabela não possui campos obrigatórios e teste passou sem cumprir seu propósito")

    def test_valid_endpoint_with_permision_and_invalid_arguments(self):
        with self.assertRaises(InvalidParametersException):
            self.api.post(self.valid_endpoint, self._invalid_dummy_params())

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.post(path, self._operador_mock)

    def test_endpoint_blob(self):
        from base64 import b64encode
        entry = self.__valid_entry.copy()
        with open(__file__, 'r') as f:
            entry['BLOBCOL'] = b64encode(f.read())

            result = self.api.put(self.valid_endpoint, entry)
            self.assertIsInstance(result, APIPUTResponse)

    def test_endpoint_clob(self):
        entry = self.valid_entry
        entry.update(
            {self.CLOB_FIELD: self._random_string(10000)}
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
        with self.assertRaises(MissingRequiredParameterException):
            self.api.put(self.valid_endpoint, {'PROJNAME': PROJNAME})

    def test_valid_endpoint_with_permission(self):
        PROJNAME = self._random_string(3)
        params = {
            self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey],
            'PROJNAME': PROJNAME
        }
        params.update(self._operador_mock)
        result = self.api.put(self.valid_endpoint, params)

        # Updated correcly with the right output ?
        self.assertIsInstance(result, APIPUTResponse)

        updated_entry = self.api.get(
            self.valid_endpoint,
            {self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey]}
        ).first()

        # Lets get it again and check if its the result is as expected
        self.assertEqual(updated_entry['PROJNAME'], PROJNAME)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.put(path, self._invalid_dummy_params())

    def test_valid_endpoint_with_valid_permission_and_invalid_parameters_types(self):
        entry = self.__valid_entry
        entry.update({'PRSTDATE': self._random_string(5)})
        with self.assertRaises(InvalidParametersException):
            self.api.put(self.valid_endpoint, entry)


class TestDELETERequest(TestAPIRequest):
    BIG_FAKE_ID = 2749873460397

    @property
    def __dummy_ids(self):
        ids = {
            'PROJETOS': {'ID_PROJETO': 100, 'COD_OPERADOR': self._random_string(3)},
            'PESSOAS': {'ID_PESSOA': 100, 'COD_OPERADOR': self._random_string(3)},
            'ALUNOS': {'ID_ALUNO': 100, 'COD_OPERADOR': self._random_string(3)},
        }
        return ids

    @property
    def __valid_entry(self):
        """
        :rtype : dict
        """
        return self.api.get(self.valid_endpoint).content[0]

    def test_valid_endpoint_with_permission(self):
        params = {self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey]}
        params.update(self._operador_mock)
        result = self.api.delete(self.valid_endpoint, params)

        self.assertTrue(result.affectedRows >= 1)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.delete(path, self.__dummy_ids[path])

    def test_invalid_endpoint(self):
        for path in self.endpoints['invalid_endpoints']:
            with self.assertRaises(InvalidEndpointException):
                self.api.delete(path, self._invalid_dummy_params())

    def test_valid_endpoint_without_pkey(self):
        with self.assertRaises(InvalidParametersException):
            self.api.delete(self.valid_endpoint, self._invalid_dummy_params())

    def test_invalid_entry(self):
        with self.assertRaises(NothingToUpdateException):
            params = {self.valid_endpoint_pkey: self.BIG_FAKE_ID}
            params.update(self._operador_mock)
            self.api.delete(self.valid_endpoint, params)


class TestProcedureSyncRequest(TestAPIRequest):
    valid_procedure = 'CriarProjetoPesquisa'
    unauthorized_procedure = 'FooProcedure'

    @property
    def mock_blob(self):
        from base64 import b64encode

        fstream = open(__file__, 'r')
        file_b64 = b64encode(fstream.read())
        fstream.close()
        return file_b64

    @property
    def mock_dataset(self):
        return {
            'ID_PROCEDENCIA': 8400145,
            'ID_INTERESSADO': 8400145,
            'ID_PROPRIETARIO': 34767,
            'ID_CRIADOR': 34767,
            "ID_PROCEDENCIA": 8400145,
            "ID_PROPRIETARIO": 34767,
            'TIPO_INTERESSADO': 20,
            'TEMPO_ARQUIVAMENTO': 1,
            'COD_OPERADOR': 666,
            'DESCR_MAIL': self._random_string(20),
            'DT_INICIAL': str(date.today()),
            'DT_REGISTRO': str(date.today()),
            'DT_FINAL': str(date.today() + timedelta(days=100)),
            'ID_PESSOA': 34767,
            'CARGA_HORARIA': 40,
            'ID_CONTRATO_RH': 8400145,
            'ID_USUARIO': 8400145,
            'TITULO': self._random_string(40),
            'ID_UNIDADE': 123,
            # 'TEM_APOIO_FINANCEIRO': 'N'
            'PROJETO_CONTEUDO_ARQUIVO': self.mock_blob,
            'PROJETO_NOME_ARQUIVO': self._random_string(20),
            'DEPARTAMENTO_CONTEUDO_ARQUIVO': self.mock_blob,
            'DEPARTAMENTO_NOME_ARQUIVO': self._random_string(20),
        }

    def test_invalid_procedure(self):
        with self.assertRaises(InvalidEndpointException):
            name = self._random_string(20)
            self.api.call_procedure(name, {})

    def test_invalid_permission(self):
        with self.assertRaises(InvalidAPIKeyException):
            data = (self.mock_dataset.copy(),)
            self.api.call_procedure(self.unauthorized_procedure, data)

    def test_json_unserializable_dataset(self):
        with self.assertRaises(TypeError):
            data = self.mock_dataset.copy()
            data['DT_INICIAL'] = date.today()
            self.api.call_procedure(self.valid_procedure, data)

    def test_uniterable_dataset(self):
        with self.assertRaises(UnhandledAPIException):
            self.api.call_procedure(self.valid_procedure, self.mock_dataset)

    def test_valid_procedure_with_permission(self):
        result = self.api.call_procedure(self.valid_procedure, (self.mock_dataset,))
        self.assertIsInstance(result, APIProcedureSyncResponse)

    def test_valid_procedure_with_fields(self):
        fields = self.mock_dataset.keys()[4:]
        result = self.api.call_procedure(self.valid_procedure, (self.mock_dataset,), fields=fields)
        self.assertIsInstance(result, APIProcedureSyncResponse)

        result_fields = result.content.keys()
        self.assertEqual(set(result_fields), set(fields))

    def test_valid_procedure_with_invalid_fields(self):
        fields = [self._random_string(6) for i in range(6)]
        result = self.api.call_procedure(self.valid_procedure, (self.mock_dataset,), fields=fields)
        self.assertIsInstance(result, APIProcedureSyncResponse)
        self.assertEqual(len(result.content), 0)

    def test_valid_procedure_with_invalid_dataset(self):
        with self.assertRaises(MissingRequiredFieldsException):
            data = {self._random_string(5): self._random_string(10) for i in range(6)}
            self.api.call_procedure(self.valid_procedure, (data,))
