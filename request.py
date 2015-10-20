# -*- coding: utf-8 -*-
import requests
from enum import Enum
from .exceptions import *
from .result import APIResultObject, APIPOSTResponse, APIPUTResponse, APIDELETEResponse


__all__ = ["UNIRIOAPIRequest"]


class APIServer(Enum):
    PRODUCTION = "https://sistemas.unirio.br/api"
    DEVELOPMENT = "https://teste.sistemas.unirio.br/api"
    LOCAL = "http://localhost:8000/api"
    PRODUCTION_DEVELOPMENT = "https://sistemas.unirio.br/api_teste"


class UNIRIOAPIRequest(object):
    """
    UNIRIOAPIRequest is the main class for
    """
    lastQuery = ""
    timeout = 5  # 5 seconds

    def __init__(self, api_key, server=APIServer.LOCAL, debug=True, cache=None):
        """

        :type server: str
        :type cache: gluon.cache.CacheInRam
        :param api_key: The 'API Key' that will the used to perform the requests
        :param server: The server that will used.
        """
        self.api_key = api_key
        self.server = server
        self.requests = []
        self.debug = debug
        self.cache = cache

    def _url_query_parameters_with_dictionary(self, params=None):
        """
        The method receiver a dictionary of URL parameters, validates and returns
        as an URL encoded string
        :rtype : dict
        :param params: The parameters for the request. A value of None will
                        send only the API_KEY and FORMAT parameters
        :return: URL enconded string with the valid parameters
        """
        if not params:
            params = {}

        params.update({"API_KEY": self.api_key, "FORMAT": "JSON"})

        for k, v in params.items():
            if not str(v):
                del params[k]
            if isinstance(v, tuple):
                params[k] = str(v)[1:-1]

        return params

    def _url_query_return_fields_with_list(self, fields=None):
        """
        The method receives a list of fields to be returned as a string of
        concatenated FIELDS parameters
        
        :rtype : dict
        :param fields: A list of strings with valid field names for selected path
        :type fields: list 
        """
        if not fields:
            fields = []

        return {'FIELDS': ','.join(fields)}

    def _url_with_path(self, path):
        """
        The method construct the base URL to be used for requests.

        :rtype : str
        :param path: The API endpoint to use for the request, for example "/ALUNOS"
        :return: Base URL with the provided endpoint
        """
        request_url = self.server + "/" + path
        return request_url

    def url_query_data(self, params=None, fields=None):
        """
        The method provides the additional data to send to the API server in order to
        perform a request.

        :rtype : str
        :param params: dictionary with URL parameters
        :param fields: list with de desired return fields. Empty list or None will return all Fields
        :return:
        """
        parameters = self._url_query_parameters_with_dictionary(params)
        return_fields = self._url_query_return_fields_with_list(fields)
        # data = parameters + returnFields if returnFields else parameters
        if return_fields:
            parameters.update(return_fields)
        return parameters

    def payload(self, params=None):
        """
        O payload de um POST/PUT obrigatoriamente devem ser do tipo dict.

        :type params: dict
        :param params: Dicionário com os dados a serem inseridos
        :rtype : dict
        :return: Dicionário processado a ser enviado para a Request
        """
        payload = dict(params)
        payload.update({
            "API_KEY": self.api_key
        })
        return payload

    def __cache_hash(self, path, params):
        """
        Método utilizado para gerar um hash único para ser utilizado como chave de um cache

        :param path: String correspondente a um endpoint
        :param params: Dicionário de parâmetros
        :return: String a ser utilizada como chave de um cache
        """
        if params:
            return path + str(hash(frozenset(params.items())))
        else:
            return path

    def get(self, path, params=None, fields=None, cache_time=0):
        """
        Método para realizar uma requisição GET. O método utiliza a API Key fornecida ao instanciar 'UNIRIOAPIRequest'
        e uma chave inválida resulta em um erro HTTP

        :type path: str
        :param path: string with an API ENDPOINT
        :type params: dict
        :param params: dictionary with URL parameters
        :type fields: list or tuple
        :param fields: list with de desired return fields. Empty list or None will return all Fields
        :type cache_time: int
        :param cache_time int for cached expiration time. 0 means no cached is applied
        :rtype : APIResultObject
        :raises Exception may raise an exception if not able to instantiate APIResultObject
        """

        def _get():
            url = self._url_with_path(path)
            payload = self.url_query_data(params, fields)
            try:
                r = requests.get(url, params=payload, verify=False)
                if self.debug:
                    print r.url
                result_object = APIResultObject(r, self)
                self.lastQuery = url
                return result_object
            except APIException as e:
                if cache_time:
                    return None
                else:
                    raise e

        if self.cache and cache_time:
            unique_hash = self.__cache_hash(path, params)
            cached_content = self.cache(
                unique_hash,
                lambda: _get(),
                time_expire=cache_time
            )
            if self.debug:
                print unique_hash
            return cached_content
        else:
            return _get()

    def post(self, path, params):
        """

        :rtype : APIPOSTResponse
        """
        url = self._url_with_path(path)
        payload = self.payload(params)

        response = requests.post(url, payload, verify=False)
        return APIPOSTResponse(response, self)

    def delete(self, path, params):
        """
        :type path: str
        :param path: string with an API ENDPOINT

        :rtype : unirio.api.result.APIDELETEResponse
        """
        url = self._url_with_path(path)
        payload = self.url_query_data(params)
        # contentURI = "%s?%s" % (url, payload)

        # gamb_payload = "&".join(["%s=%s" % (campo, payload[campo]) for campo in payload])
        # contentURI = "%s?%s" % (url,gamb_payload)
        req = requests.delete(url, data=payload, verify=False)
        r = APIDELETEResponse(req, self)

        return r

    def put(self, path, params):
        """
        :type path: str
        :param path: string with an API ENDPOINT
        :type params: dict
        :param params: dictionary with URL parameters
        :rtype APIPUTResponse
        """
        url = self._url_with_path(path)
        payload = self.payload(params)
        response = requests.put(url, payload, verify=False)

        return APIPUTResponse(response, self)
