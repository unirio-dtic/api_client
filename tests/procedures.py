# coding=utf-8
from datetime import timedelta, date
from unirio.api.exceptions import *
from unirio.api.result import *
from tests.request import TestAPIRequest


class TestProcedureSyncRequest(TestAPIRequest):
    valid_procedure = 'FooProcedure'
    unauthorized_procedure = 'CriarProjetoPesquisa'

    @property
    def mock_blob(self):
        from base64 import b64encode

        fstream = open(__file__, 'r')
        file_b64 = b64encode(fstream.read())
        fstream.close()
        return file_b64

    @property
    def mock_dataset(self):
        # todo: Melhorar mock
        return {
            'ID_UNIT_TEST': 9999,
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
