# -*- coding: utf-8 -*-
import urllib

class UNIRIOAPIRequest(object):
    """
    UNIRIOAPIRequest is the main class for
    """
    method = "GET"
    lastQuery = ""
    _versions = { 0 : "Production", 1 : "Development" }
    baseAPIURL = { 0 : "https://sistemas.unirio.br/api", 1 : "https://teste.sistemas.unirio.br/api" }

    def __init__( self, api_key, server=0 ):
        self.api_key = api_key
        self.server = server

    def _URLQueryParametersWithDictionary( self, params ):
        params.update( {"API_KEY" : self.api_key} )
        return urllib.urlencode( params )

    def _URLQueryReturnFieldsWithArray( self, fields):
        if( len( fields )>0 ):
            return '&FIELDS=' + ','.join( fields )

    def _URLWithPath( self, path ):
        APIURL = self.baseAPIURL[ self.server ]
        requestURL = APIURL + "/" + path
        return requestURL

    def URLQueryData(self, params, fields):
        parameters = self._URLQueryParametersWithDictionary(params)
        returnFields = self._URLQueryReturnFieldsWithArray(fields)
        data = parameters + returnFields if returnFields else parameters
        return data

    #===========================================================================
    # Método para realizar uma requisição GET. O método utiliza a API Key
    # fornecida ao instanciar 'UNIRIOAPIRequest' e uma chave inválida resulta
    # em um erro HTTP
    #===========================================================================
    def performGETRequest( self, path, params, fields=[] ):
        from apiresult import APIResultObject
        url = self._URLWithPath(path)
        data = self.URLQueryData(params, fields)

        try:
            json = urllib.urlopen(url, data).read()
            resultObject = APIResultObject(json, self)
            self.lastQuery = url + "?" + data
            return resultObject.content
        except Exception as e:
            raise e

    def performPOSTRequest( self, path, params ):
        pass

    def _URLQueryParametersForReturnFields( self, fields):
        pass