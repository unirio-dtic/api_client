# -*- coding: utf-8 -*-
from gluon.contrib import simplejson

class APIResultObject(object):
    count = 0
    lmin = 0
    lmax = 0
    content = []

    def __init__(self, json, APIRequest):
        r = simplejson.loads( json )
        self.content = r["content"]
        self.lmin = r["subset"][0]
        self.lmax = r["subset"][1]
        self.request = APIRequest

    #===========================================================================
    # Um subset de um resultado (lmin->lmax) pode conter somente
    # uma parte do total de resultados (count). Este método retornará
    # os parâmetros a serem utilizados pelo próximo UNIRIOAPI.performRequest
    #===========================================================================
    def nextRequestForResult(self):
        pass

