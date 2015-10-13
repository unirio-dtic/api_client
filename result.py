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


class APIResultObject(object):
    lmin = 0
    lmax = 0
    content = []

    def __init__(self, r, api_request):
        """
        :type r: Response
        :type self.content: list
        :type self.lmin: int
        :type self.lmax: int
        :type self.count: int
        :param r:
        :param api_request:
        :raise ValueError:
        """
        if http.OK == r.status_code:
            try:
                json = r.json()
                self.content = json["content"]
                self.fields = tuple(k for k in self.content[0].keys())
                self.lmin = json["subset"][0]
                self.lmax = json["subset"][1]
            except ValueError:
                raise ValueError("JSON decoding failed. Value may be None.")

        elif http.FORBIDDEN == r.status_code:
            raise ForbiddenEndpointException(r, r.text, r.status_code)
        elif http.NOT_FOUND == r.status_code:
            raise InvalidEndpointException(r, r.text, r.status_code)
        self.request = api_request

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


class APIPOSTResponse(object):
    def __init__(self, response, request):
        """

        :type response: Response
        :type request: unirio.api.request.UNIRIOAPIRequest
        :param response:
        :param request:
        :raise Exception: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        self.response = response
        if not response.status_code == 201:
            raise POSTException("Erro %d - %s" % (self.response.status_code, self.response.content))

        self.request = request
        self.insertId = self.response.headers['id']
        print "Inseriou em %s com a ID %s" % (self.response.headers['Location'], self.insertId)

    def new_content_uri(self):
        return self.response.headers['Location'] + "&API_KEY=" + self.request.api_key


class APIPUTResponse(object):
    def __init__(self, response, request):
        """

        :type response: Response
        :param response:
        :param request:
        :raise Exception: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        self.response = response
        if not response.status_code == 200:
            raise PUTException("Erro %d - %s" % (self.response.status_code, self.response.content))

        self.request = request
        self.affectedRows = self.response.headers['Affected']


class APIDELETEResponse(APIPUTResponse):
    def __init__(self, response, request):
        try:
            super(APIDELETEResponse, self).__init__(response, request)
        except PUTException:
            raise DELETEException
