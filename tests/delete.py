# coding=utf-8
from unirio.api import APIDELETEResponse

from tests import config
from unirio.api.exceptions import *
from tests.request import TestAPIRequest
from tests.post import TestPOSTRequest


class TestDELETERequest(TestAPIRequest):
    BIG_FAKE_ID = 2749873460397

    def setUp(self):
        super(TestDELETERequest, self).setUp()
        self.api.post(self.valid_endpoint, TestPOSTRequest.valid_entry())

    @property
    def __dummy_ids(self):
        ids = {
            'PROJETOS': {'ID_PROJETO': 100, 'COD_OPERADOR': 999},
            'PESSOAS': {'ID_PESSOA': 100, 'COD_OPERADOR': 999},
            'ALUNOS': {'ID_ALUNO': 100, 'COD_OPERADOR': 999},
        }
        return ids

    def __valid_entry(self):
        """
        :rtype : dict
        """
        return self.api.get_single_result(self.valid_endpoint)

    def test_valid_endpoint_with_permission(self):
        params = {self.valid_endpoint_pkey: self.__valid_entry()[self.valid_endpoint_pkey]}
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

    def test_case_insensibility(self):
        for case in config.STR_CASES:
            params = {self.valid_endpoint_pkey: self.__valid_entry()[self.valid_endpoint_pkey]}
            params.update(self._operador_mock)

            result = self.api.delete(self.valid_endpoint, self._convert_entry_keys_case(case, params))

            assert isinstance(result, APIDELETEResponse)
            assert result.affectedRows == 1
