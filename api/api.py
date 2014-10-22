# -*- coding: utf-8 -*-
import urllib
import httplib
from twisted.web.http_headers import Headers
from apiresult import APIResultObject


class UNIRIOAPIRequest(object):
    """
    UNIRIOAPIRequest is the main class for
    """
    method = "GET"
    lastQuery = ""
    _versions = {0: "Production", 1: "Development"}
    baseAPIURL = {0: "https://sistemas.unirio.br/api", 1: "https://teste.sistemas.unirio.br/api"}
    timeout = 5  # 5 seconds

    def __init__(self, api_key, server=0):
        self.api_key = api_key
        self.server = server

    def _URLQueryParametersWithDictionary(self, params={}):
        params.update({"API_KEY": self.api_key, "FORMAT": "JSON"})
        for k, v in params.items():
            if not str(v):
                del params[k]
        return urllib.urlencode(params)

    def _URLQueryReturnFieldsWithList(self, fields=[]):
        """

        :rtype : str
        :param fields: A list of strings with valid field names for selected path
        :type fields: list 
        """
        if ( len(fields) > 0 ):
            return '&FIELDS=' + ','.join(fields)

    def _URLWithPath(self, path):
        APIURL = self.baseAPIURL[self.server]
        requestURL = APIURL + "/" + path
        return requestURL

    def URLQueryData(self, params, fields=None):
        parameters = self._URLQueryParametersWithDictionary(params)
        returnFields = self._URLQueryReturnFieldsWithList(fields)
        data = parameters + returnFields if returnFields else parameters
        return data

    def performGETRequest(self, path, params={}, fields=[]):
        """
        Método para realizar uma requisição GET. O método utiliza a API Key
        fornecida ao instanciar 'UNIRIOAPIRequest' e uma chave inválida resulta
        em um erro HTTP

        :param path: string with an API ENDPOINT
        :param params: dictionary with URL parameters
        :param fields: list with de desired return fields. Empty list or None will return all Fields
        :rtype : APIResultObject
        :raises Exception may raise an exception if not able to instantiate APIResultObject
        """

        url = self._URLWithPath(path) + "?" + self.URLQueryData(params, fields)

        try:
            json = urllib.urlopen(url).read()
            resultObject = APIResultObject(json, self)
            self.lastQuery = url
            return resultObject
        except Exception as e:
            raise e

    def performPOSTRequest(self, path, params):
        http = httplib.HTTPConnection(self.baseAPIURL[self.server], httplib.HTTPS_PORT, timeout=self.timeout)
        url = self._URLWithPath(path)
        headers = {"Content-Type": "application/json"}
        data = self.URLQueryData(params)

        http.request("POST", url, data, headers)
        response = http.getresponse()

        return APIPOSTResponse(response.read(), self)


    def performDELETERequest(self, path, params):
        pass

    def performUPDATERequest(self):
        pass
