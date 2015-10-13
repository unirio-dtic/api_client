__author__ = 'diogomartins'


class APIException(Exception):
    def __init__(self, response, msg=None, status_code=None):
        """
        :type response: requests.models.Response
        """
        self.response = response
        self.msg = msg
        self.status_code = status_code


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
