from enum import Enum
from .result import APIResultObject, APIPOSTResponse, APIPUTResponse, APIDELETEResponse, APIProcedureResponse
from typing import Dict, Any, Iterable


class APIServer(Enum):
    def __getattr__(self, item) -> str:
        pass


class UNIRIOAPIRequest(object):
    def __init__(self, api_key: str, server: APIServer, debug: bool, cache=None):
        pass

    def get(self, path: str, params: Dict[str:Any]=None, fields: list=None, cache_time: int=0) -> APIResultObject:
        pass

    def post(self, path: str, params: Dict[str:Any]) -> APIPOSTResponse:
        pass

    def delete(self, path: str, params: Dict[str:int]) -> APIDELETEResponse:
        pass

    def put(self, path: str, params: Dict[str:Any]) -> APIPUTResponse:
        pass

    def call_procedure(self, name: str, data: Iterable[Dict[str:Any]], fields: list=None, async: bool=False, ws_group: str=None) -> APIProcedureResponse:
        pass
