# -*- coding: utf-8 -*-
import urllib
import httplib
from twisted.web.http_headers import Headers
from apiresult import APIResultObject, APIPOSTResponse

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
        """

        :param api_key: The 'API Key' that will the used to perform the requests
        :param server: The server that will used. Production or Development
        """
        self.api_key = api_key
        self.server = server

    def _URLQueryParametersWithDictionary(self, params=None):
        """
        The method receiver a dictionary of URL parameters, validates and returns
        as an URL encoded string
        :rtype : str
        :param params: The parameters for the request. A value of None will
                        send only the API_KEY and FORMAT parameters
        :return: URL enconded string with the valid parameters
        """
        if not params: params = {}

        params.update({"API_KEY": self.api_key, "FORMAT": "JSON"})

        for k, v in params.items():
            if not str(v):
                del params[k]
        return urllib.urlencode(params)

    def _URLQueryReturnFieldsWithList(self, fields=None):
        """
        The method receives a list of fields to be returned as a string of
        concatenated FIELDS parameters
        
        :rtype : str
        :param fields: A list of strings with valid field names for selected path
        :type fields: list 
        """
        if not fields: fields = []
        if ( len(fields) > 0 ):
            return '&FIELDS=' + ','.join(fields)

    def _URLWithPath(self, path):
        """
        The method construct the base URL to be used for requests.

        :rtype : str
        :param path: The API endpoint to use for the request, for example "/ALUNOS"
        :return: Base URL with the provided endpoint
        """
        APIURL = self.baseAPIURL[self.server]
        requestURL = APIURL + "/" + path
        return requestURL

    def URLQueryData(self, params=None, fields=None):
        """
        The method provides the additional data to send to the API server in order to
        perform a request.

        :rtype : str
        :param params: dictionary with URL parameters
        :param fields: list with de desired return fields. Empty list or None will return all Fields
        :return:
        """
        parameters = self._URLQueryParametersWithDictionary(params)
        returnFields = self._URLQueryReturnFieldsWithList(fields)
        data = parameters + returnFields if returnFields else parameters

        return data

    def performGETRequest(self, path, params=None, fields=None):
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
