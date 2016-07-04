# -*- coding: utf-8 -*-
import requests
import logging
from enum import Enum
from .exceptions import *
from .result import *
from collections import Iterable
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def requires(params):
    def decorator(fn):
        def checker(*args, **kwargs):
            def validate(param):
                if param not in args[2]:
                    raise MissingRequiredParameterException(args[0], param)
            if isinstance(params, str):
                validate(params)
            elif isinstance(params, Iterable):
                for param in params:
                    validate(param)
            else:
                raise TypeError('params must be str or Iterable.')
            return fn(*args, **kwargs)
        return checker
    return decorator


class APIServer(Enum):
    PRODUCTION = "https://sistemas.unirio.br/api"
    DEVELOPMENT = "https://teste.sistemas.unirio.br/api"
    LOCAL = "http://localhost:8000/api"
    PRODUCTION_DEVELOPMENT = "https://sistemas.unirio.br/api_teste"


class UNIRIOAPIRequest(object):
    """
    UNIRIOAPIRequest is the main class for
    """

    def __init__(self, api_key, server=APIServer.LOCAL, debug=True, cache=None, cert=False):
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
        self.last_request = ""
        self.cert = cert

    def _url_query_parameters_with_dictionary(self, params={}):
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

        params.update(self._payload)
        params.update({"FORMAT": "JSON"})

        for k, v in params.items():
            if v is None or not str(v):
                raise NullParameterException(None, msg="Parâmetro passado é nulo.", invalid_parameters=k)

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

    def _url_query_data(self, params=None, fields=None):
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

    @property
    def _payload(self):
        """
        O payload de um POST/PUT obrigatoriamente devem ser do tipo dict.

        :type params: dict
        :param params: Dicionário com os dados a serem inseridos
        :rtype : dict
        :return: Dicionário processado a ser enviado para a Request
        """
        return {"API_KEY": self.api_key}

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

    def get(self, path, params=None, fields=None, cache_time=0, bypass_no_content_exception=False):
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
        :type bypass_no_content_exception: bool
        :param bypass_no_content_exception: optional argument to indicate to return a empty list instead of raising a NoContentException
        :rtype : APIResultObject
        :raises Exception may raise an exception if not able to instantiate APIResultObject
        """
        def _get():
            url = self._url_with_path(path)
            payload = self._url_query_data(params, fields)

            r = requests.get(url, params=payload, verify=self.cert)
            if self.debug:
                logging.debug(r.url)
                self.last_request = url
            try:
                result_object = APIResultObject(r, self)
            except NoContentException as e:
                if bypass_no_content_exception:
                    return []
                raise e
            return result_object

        if self.cache and cache_time:
            unique_hash = self.__cache_hash(path, params)
            cached_content = self.cache(
                unique_hash,
                lambda: _get(),
                time_expire=cache_time
            )
            if self.debug:
                logging.debug(unique_hash)
            return cached_content
        else:
            return _get()

    def get_single_result(self, path, params=None, fields=None, cache_time=0, bypass_no_content_exception=False):
        """
        Wrapper para pegar apenas um resultado.

        :param path:
        :param params:
        :param fields:
        :param cache_time:
        :param bypass_no_content_exception:
        :rtype: dict
        """
        try:
            if not params:
                params = {}

            params.update({
                "LMIN": 0,
                "LMAX": 1
            })

            res = self.get(path, params, fields, cache_time)
            return res.first()
        except NoContentException as e:
            if bypass_no_content_exception:
                return None
            raise e

    @requires('COD_OPERADOR')
    def post(self, path, params):
        """

        :rtype : APIPOSTResponse
        """
        url = self._url_with_path(path)
        params.update(self._payload)

        response = requests.post(url, params, verify=self.cert)
        return APIPOSTResponse(response, self)

    @requires('COD_OPERADOR')
    def delete(self, path, params):
        """
        :type path: str
        :param path: string with an API ENDPOINT

        :rtype : unirio.api.result.APIDELETEResponse
        """
        url = self._url_with_path(path)
        payload = self._url_query_data(params)
        # contentURI = "%s?%s" % (url, payload)

        # gamb_payload = "&".join(["%s=%s" % (campo, payload[campo]) for campo in payload])
        # contentURI = "%s?%s" % (url,gamb_payload)
        req = requests.delete(url, data=payload, verify=self.cert)
        r = APIDELETEResponse(req, self)

        return r

    @requires('COD_OPERADOR')
    def put(self, path, params):
        """
        :type path: str
        :param path: string with an API ENDPOINT
        :type params: dict
        :param params: dictionary with URL parameters
        :rtype APIPUTResponse
        """
        url = self._url_with_path(path)
        params.update(self._payload)

        if not isinstance(params, dict):
            params = dict(params)  # todo: Fix para casos de CaseInsensitiveDict que não é serializable

        response = requests.put(url, params, verify=self.cert)

        return APIPUTResponse(response, self)

    def call_procedure(self, name, data, fields=None, async=False, ws_group=None):
        """
        :type fields: tuple or list
        :param fields: list with de desired return fields. Empty list or None will return all
        :param name: Procedure name to be called
        :type name: str
        :param data: Data to be serialized
        :type data: list or tuple
        :type async: bool
        :param ws_group: The Websocket group that the async response should be posted
        :type ws_group: str
        """
        url = self._url_with_path("procedure/" + name)
        _data = dict(data=data,
                     async=async,
                     fields=fields or [],
                     **self._payload)
        response = requests.post(url, json=_data, verify=self.cert)

        if async:
            return APIProcedureAsyncResponse(response, self, ws_group)

        return APIProcedureSyncResponse(response, self)
