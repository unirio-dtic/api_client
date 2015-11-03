# coding=utf-8
__author__ = 'diogomartins'


class APIException(Exception):
    def __init__(self, response, msg=None):
        """
        :type response: requests.models.Response
        """
        self.response = response
        self.msg = msg


class ForbiddenEndpointException(APIException):
    pass


class InvalidEndpointException(APIException):
    pass


class ContentNotCreatedException(APIException):
    pass


class InvalidAPIKeyException(APIException):
    pass


class NoContentException(APIException, ValueError):
    pass


class ContentNotFoundException(APIException):
    pass


class InvalidEncodingException(APIException):
    def __init__(self, response, msg=None, invalid_field=None):
        """

        :type invalid_field: list or tuple
        """
        super(InvalidEncodingException, self).__init__(response, msg)
        self.invalid_field = invalid_field

class InvalidParametersException(APIException):
    def __init__(self, response, msg=None, invalid_parameters=None):
        """
        Pode ser tipo de dado inválido ou parâmetro incompatível
        :type invalid_parameters: list or tuple
        """
        super(InvalidParametersException, self).__init__(response, msg)
        self.invalid_parameters = invalid_parameters


class NothingToUpdateException(APIException):
    pass


class UnhandledAPIException(APIException):
    pass


class MissingPrimaryKeyException(APIException):
    pass
