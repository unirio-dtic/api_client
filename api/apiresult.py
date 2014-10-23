# -*- coding: utf-8 -*-
from gluon.contrib import simplejson


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


class APIPOSTResponse(APIResultObject):
    pass