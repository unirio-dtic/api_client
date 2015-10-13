__author__ = 'diogomartins'


class APIException(Exception):
    def __init__(self, response):
        self.response = response


class ForbiddenEndpointException(APIException):
    def __init__(self, response, msg=None, status_code=None):
        super(ForbiddenEndpointException, self).__init__(response)
        self.msg = msg
        self.status_code = status_code


class InvalidEndpointException(APIException):
    def __init__(self, response, msg=None, status_code=None):
        super(InvalidEndpointException, self).__init__(response)
        self.msg = msg
        self.status_code = status_code