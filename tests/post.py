# coding=utf-8
from unirio.api.exceptions import *
from unirio.api.result import *
from tests.request import TestAPIRequest


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

        entry = self.valid_entry.copy()

        with open(__file__, 'r') as f:
            entry['BLOBCOL'] = b64encode(f.read())

            result = self.api.post(self.valid_endpoint, entry)
            self.assertIsInstance(result, APIPOSTResponse)

    def test_endpoint_clob(self):
        entry = self.valid_entry
        entry.update(
            {self.CLOB_FIELD: self._random_string(10000)}
        )
        new_resource = self.api.post(self.valid_endpoint, entry)

        self.assertIsInstance(new_resource, APIPOSTResponse)
