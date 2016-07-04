# -*- coding: utf-8 -*-
try:
    import httplib as http
except ImportError:
    import http.client as http
from .exceptions import *
import json
from collections import Iterable, Sized
from requests.structures import CaseInsensitiveDict


__all__ = ('APIResponse', 'APIResultObject', 'APIDELETEResponse', 'APIPOSTResponse', 'APIPUTResponse',
           'APIProcedureSyncResponse', 'APIProcedureAsyncResponse')


class APIResponse(object):
    def __init__(self, response, request):
        """
        :type response: requests.models.Response
        :raises APIException
        """
        self.response = response
        self.request = request
        # TODO Como diferir dois casos de bad request ?
        if http.OK == self.response.status_code:
            pass
        elif http.BAD_REQUEST == self.response.status_code and self.response.headers.get('InvalidParameters', False):
            raise InvalidParametersException(self.response, json.loads(self.response.headers['InvalidParameters']))
        elif http.BAD_REQUEST == self.response.status_code and self.response.headers.get('InvalidEncoding', False):
            raise InvalidEncodingException(self.response, json.loads(self.response.headers['InvalidEncoding']))
        else:
            common_errors = {
                http.FORBIDDEN: ForbiddenEndpointException(self.response),
                http.UNAUTHORIZED: InvalidAPIKeyException(self.response),
                http.INTERNAL_SERVER_ERROR: UnhandledAPIException(self.response),
                http.NOT_FOUND: InvalidEndpointException(self.response)
            }
            try:
                raise common_errors[self.response.status_code]
            except KeyError:
                pass


class APIResultObject(APIResponse, Iterable, Sized):
    lmin = 0
    lmax = 0
    content = []

    def __init__(self, response, request):
        """
            :type r: Response
            :type self.content: list
            :type self.lmin: int
            :type self.lmax: int
            :type self.count: int
            :raises APIException, ValueError:
            """
        super(APIResultObject, self).__init__(response, request)
        if http.OK == self.response.status_code:
            try:
                json = self.response.json(object_hook=CaseInsensitiveDict)
                self.content = json["content"]
                self.fields = tuple(k for k in self.content[0].keys())
                self.lmin = json["subset"][0]
                self.lmax = json["subset"][1]
            except ValueError:
                raise NoContentException(self.response)

    def next_request_for_result(self):
        """
        Um subset de um resultado (lmin->lmax) pode conter somente
        uma parte do total de resultados (count). Este método retornará
        os parâmetros a serem utilizados pelo próximo UNIRIOAPI.performRequest

        """
        pass

    def first(self):
        """
        Método de conveniência para retornar o primeiro dicionário de content

        :rtype : dict
        """
        return self.content[0]

    def __iter__(self):
        for item in self.content:
            yield item

    def __getitem__(self, item):
        return self.content[item]

    def __len__(self):
        return len(self.content)


class APIPOSTResponse(APIResponse):
    def __init__(self, response, request):
        """
        :type response: requests.models.Response
        :type request: unirio.api.request.UNIRIOAPIRequest
        :param response:
        :param request:
        :raises APIException: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        super(APIPOSTResponse, self).__init__(response, request)
        if http.CREATED == response.status_code:
            self.request = request
            self.insertId = self.response.headers['id']
            if self.request.debug:
                print("Inseriu em %s com a ID %s" % (self.response.headers['Location'], self.insertId))
        else:
            errors = {
                http.NOT_FOUND:     ContentNotCreatedException(self.response),  # TODO api retornando status code errado para esse caso
                http.BAD_REQUEST:   InvalidParametersException(self.response)
            }
            raise errors[self.response.status_code]

    def new_content_uri(self):
        return self.response.headers['Location'] + "&API_KEY=" + self.request.api_key


class APIProcedureResponse(APIResponse):
    def __init__(self, response, request):
        super(APIProcedureResponse, self).__init__(response, request)
        if http.BAD_REQUEST == response.status_code:
            raise MissingRequiredFieldsException(self.response, self.response.text)
        elif not http.CREATED == response.status_code:
            raise NotImplementedError("Esse erro era desconhecido. Analise o motivo e a necessidade de novo tipo de exception")


class APIProcedureSyncResponse(APIProcedureResponse):
    def __init__(self, response, request):
        super(APIProcedureSyncResponse, self).__init__(response, request)
        self.content = self.response.json()


class APIProcedureAsyncResponse(APIProcedureResponse):
    def __init__(self, response, request, ws_group):
        super(APIProcedureAsyncResponse, self).__init__(response, request)
        self.ws_group = ws_group
        json = self.response.json()
        self.accepted = []
        self.refused = []
        raise NotImplementedError


class APIPUTResponse(APIResponse):
    def __init__(self, response, request):
        """
        :type response: Response
        :param response:
        :param request:
        :raises APIException
        """
        super(APIPUTResponse, self).__init__(response, request)
        if http.OK == self.response.status_code:
            self.request = request
            # todo: Pode ser OK e não ter affectedRows em caso de update de blob. Relacionado a issue do server
            self.affectedRows = self.response.headers.get('Affected')

        else:
            errors = {
                http.NOT_FOUND:             ContentNotFoundException(self.response),
                http.UNPROCESSABLE_ENTITY:  InvalidParametersException(self.response),
                http.NO_CONTENT:            NothingToUpdateException(self.response),
                http.BAD_REQUEST:           MissingPrimaryKeyException(self.response)
            }
            raise errors[self.response.status_code]


class APIDELETEResponse(APIResponse):
    def __init__(self, response, request):
        """
        :raises APIException
        """
        super(APIDELETEResponse, self).__init__(response, request)
        if http.OK == self.response.status_code:
            self.affectedRows = int(self.response.headers['Affected'])
        else:
            errors = {
                http.NOT_FOUND:     ContentNotFoundException(self.response),
                http.NO_CONTENT:    NothingToUpdateException(self.response),
                http.BAD_REQUEST:   MissingPrimaryKeyException(self.response)
            }
            raise errors[self.response.status_code]
