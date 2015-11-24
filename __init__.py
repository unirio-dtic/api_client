from .request import UNIRIOAPIRequest, APIServer
from .result import APIResultObject
import abc


class Usuario:
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def id_usuario(self): pass
