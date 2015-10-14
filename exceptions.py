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


class InvalidParametersException(APIException):
    pass


class NothingToUpdateException(APIException):
    pass


class UnhandledAPIException(APIException):
    pass


class MissingPrimaryKeyException(APIException):
    pass