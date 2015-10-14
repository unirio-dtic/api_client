# -*- coding: utf-8 -*-
try:
    import httplib as http
except ImportError:
    import http.client as http

from .exceptions import *

__all__ = [
    "APIException",
    "APIResultObject",
    "APIPOSTResponse",
    "APIPUTResponse",
    "APIDELETEResponse"
]


class APIResponse(object):
    def __init__(self, response, request):
        """
        :type response: requests.models.Response
        """
        self.response = response
        self.request = request
        if http.FORBIDDEN == self.response.status_code:
            raise ForbiddenEndpointException(self.response)
        elif http.UNAUTHORIZED == self.response.status_code:
            raise InvalidAPIKeyException(self.response)
        elif http.INTERNAL_SERVER_ERROR == self.response.status_code:
            raise UnhandledAPIException(self.response)


class APIResultObject(APIResponse):
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
            :raise ValueError:
            """
        super(APIResultObject, self).__init__(response, request)
        if http.OK == self.response.status_code:
            try:
                json = self.response.json()
                self.content = json["content"]
                self.fields = tuple(k for k in self.content[0].keys())
                self.lmin = json["subset"][0]
                self.lmax = json["subset"][1]
            except ValueError:
                raise NoContentException(self.response)

        elif http.NOT_FOUND == self.response.status_code:
            raise InvalidEndpointException(self.response)

    def next_request_for_result(self):
        """
        Um subset de um resultado (lmin->lmax) pode conter somente
        uma parte do total de resultados (count). Este método retornará
        os parâmetros a serem utilizados pelo próximo UNIRIOAPI.performRequest

        """
        pass

    def first(self):
        """
        Método de conveniência para retornar o primeiro dicionário de content ou None, caso o conteúdo seja vazio

        :rtype : dict
        """
        if not self.content:
            return None
        return self.content[0]


class APIPOSTResponse(APIResponse):
    def __init__(self, response, request):
        """
        :type response: requests.models.Response
        :type request: unirio.api.request.UNIRIOAPIRequest
        :param response:
        :param request:
        :raise Exception: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        super(APIPOSTResponse, self).__init__(response, request)
        if http.CREATED == response.status_code:
            self.request = request
            self.insertId = self.response.headers['id']
            print "Inseriu em %s com a ID %s" % (self.response.headers['Location'], self.insertId)
        elif http.NOT_FOUND == self.response.status_code:  # TODO api retornando status code errado para esse caso
            raise ContentNotCreatedException(self.response)
        elif http.BAD_REQUEST == self.response.status_code:
            raise InvalidParametersException(self.response)

    def new_content_uri(self):
        return self.response.headers['Location'] + "&API_KEY=" + self.request.api_key


class APIPUTResponse(APIResponse):
    def __init__(self, response, request):
        """
        :type response: Response
        :param response:
        :param request:
        :raise Exception: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        super(APIPUTResponse, self).__init__(response, request)
        if http.OK == self.response.status_code:
            self.request = request
            self.affectedRows = self.response.headers['Affected']
        elif http.NOT_FOUND == self.response.status_code:
            raise ContentNotFoundException(self.response)
        elif http.UNPROCESSABLE_ENTITY == self.response.status_code:
            raise InvalidParametersException(self.response)
        elif http.NO_CONTENT == self.response.status_code:
            raise NothingToUpdateException(self.response)
        elif http.BAD_REQUEST == self.response.status_code:
            raise MissingPrimaryKeyException(self.response)


class APIDELETEResponse(APIResponse):
    def __init__(self, response, request):
        super(APIDELETEResponse, self).__init__(response, request)
        if http.OK == self.response.status_code:
            self.affectedRows = int(self.response.headers['Affected'])
        elif http.NOT_FOUND == self.response.status_code:
            raise ContentNotFoundException(self.response)
        elif http.NO_CONTENT == self.response.status_code:
            raise NothingToUpdateException(self.response)
        elif http.BAD_REQUEST == self.response.status_code:
            raise MissingPrimaryKeyException(self.response)