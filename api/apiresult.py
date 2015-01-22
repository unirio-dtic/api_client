# -*- coding: utf-8 -*-
from gluon.contrib import simplejson

__all__ = [
    "APIException",
    "APIResultObject",
    "APIPOSTResponse",
    "APIPUTResponse"
]


class APIException(Exception):
    pass


class APIResultObject(object):
    count = 0
    lmin = 0
    lmax = 0
    content = []

    def __init__(self, json, APIRequest):
        try:
            r = simplejson.loads(json)
            self.content = r["content"]
            self.lmin = r["subset"][0]
            self.lmax = r["subset"][1]
            self.count = r["count"]
        except ValueError:
            raise ValueError("JSON decoding failed. Value may be None.")
        self.request = APIRequest

    def nextRequestForResult(self):
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
    #TODO Inserir definição da classe
    def __init__(self, response, request):
        """

        :type response: Response
        :type request: unirio.api.apirequest.UNIRIOAPIRequest
        :param response:
        :param request:
        :raise Exception: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        self.response = response
        if not response.status_code == 201:
            raise Exception("Erro %d - %s" % (self.response.status_code, self.response.content))

        self.request = request
        self.insertId = self.response.headers['id']
        print "Inseriou em %s com a ID %s" % (self.response.headers['Location'], self.insertId)

    def newContentURI(self):
        return self.response.headers['Location'] + "&API_KEY=" + self.request.api_key


class APIPUTResponse(object):
    def __init__(self, response, request):
        """

        :type response: Response
        :type response: UNIRIOAPIRequest
        :param response:
        :param request:
        :raise Exception: Uma exception é disparada caso, por algum motivo, o conteúdo não seja criado
        """
        self.response = response
        if not response.status_code == 200:
            raise APIException("Erro %d - %s" % (self.response.status_code, self.response.content))

        self.request = request
        self.affectedRows = self.response.headers['Affected']