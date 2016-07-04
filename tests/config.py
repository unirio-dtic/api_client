# coding=utf-8
from unirio.api import APIServer
from enum import Enum


# Chaves com permissão somente no endpoint unit_test e procedure FooProcedure
class Keys(Enum):
    PRODUCTION = '94ebdcee824a8fc9876c4c0b22580540a8d2330da2ec089d2e396afce2ee20332383a2df43936763358021ef9d163a21'
    PRODUCTION_DEVELOPMENT = '1a404993f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07fdfbe0587c6ef14e5c92'
    DEVELOPMENT = '1a404993f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07fdfbe0587c6ef14e5c92'
    LOCAL = '1a404993f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07fdfbe0587c6ef14e5c92'
    INVALID = 'INVALIDA_93f3175002c90738a4e46b1d12c06ddcc42f01ffbbaecf3285b98f34dc3ac0b9db9e07f0587c6ef14e5c93'


ENV = 'PRODUCTION_DEVELOPMENT'

SERVER = APIServer[ENV].value

KEY = Keys[ENV].value