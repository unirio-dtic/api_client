# coding=utf-8
from tests import config
from unirio.api.exceptions import *
from unirio.api.result import *
from tests.request import TestAPIRequest


class TestPOSTRequest(TestAPIRequest):
    @staticmethod
    def valid_entry():
        return {k: TestAPIRequest.random_string(3) for k in config.NOT_NULL_KEYS}

    def test_valid_endpoint_with_permission(self):
        new_resource = self.api.post(self.valid_endpoint, self.valid_entry())
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
        entry = self.valid_entry()

        entry['BLOBCOL'] = self.mock_blob()

        result = self.api.post(self.valid_endpoint, entry)
        self.assertIsInstance(result, APIPOSTResponse)

    def test_endpoint_clob(self):
        entry = self.valid_entry()
        entry.update(
            {self.CLOB_FIELD: self.random_string(10000)}
        )
        new_resource = self.api.post(self.valid_endpoint, entry)

        self.assertIsInstance(new_resource, APIPOSTResponse)

    def test_case_insensibility(self):
        results = []
        entry = self.valid_entry()

        for case in config.STR_CASES:
            mock = self._convert_entry_keys_case(case, entry)
            _id = self.api.post(self.valid_endpoint, mock).insertId
            result = self.api.get_single_result(self.valid_endpoint, {self.valid_endpoint_pkey: _id})

            del result[self.valid_endpoint_pkey]    # remove chave primária para comparação
            results.append(result)

        assert all(r == results[0] for r in results)
