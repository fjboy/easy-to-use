import contextlib
import json
import logging
import ssl
from http import client as http_client

LOG = logging.getLogger(__name__)


class UnknownException(Exception):
    _message = 'Unknown exception'

    def __init__(self, **kwargs):
        super(UnknownException, self).__init__(
            self._message.format(**kwargs)
        )


class HTTPException(UnknownException):
    _message = 'Unknown Http Exception'


class InvalidRequest(HTTPException):
    _message = 'InvalidRequest'


class Unauthorized(HTTPException):
    _message = 'Unauthorized'


class NotFound(HTTPException):
    _message = 'RequestNotFoud'


class Forbident(HTTPException):
    _message = 'Forbident'


class Timeout(HTTPException):
    _message = 'Timeout'


class ResourceForbident(HTTPException):
    _message = 'ResourceForbident'


class InternalServerError(HTTPException):
    _message = 'InternalServerError'


class Response(object):

    def __init__(self, status, headers, content):
        self.status = status
        self.headers = headers
        self._content = content

    @property
    def content(self):
        if self._content:
            if isinstance(self._content, dict):
                return self._content

            with contextlib.suppress(ValueError):
                return json.loads(self._content)

        return self._content

    def __str__(self):
        return f'[{self.status}] headers={self.headers}, ' \
                ' content={self._content}'


class RestClient(object):
    ERROR_CODES = {
        400: InvalidRequest,
        401: Unauthorized,
        403: Forbident,
        404: NotFound,
        405: ResourceForbident,
        408: Timeout,
        500: InternalServerError
    }

    def __init__(self, host, port=80, scheme='http', timeout=60):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.timeout = timeout
        if self.scheme not in ['http', 'https']:
            raise ValueError("scheme must be http or https")

        if self.scheme == 'https':
            ssl._create_default_https_context = ssl._create_unverified_context
            self.connection = http_client.HTTPSConnection(self.host, self.port,
                                                          timeout=self.timeout)
        else:
            self.connection = http_client.HTTPConnection(self.host, self.port,
                                                         timeout=self.timeout)

    @property
    def endpoint(self):
        return f'{self.scheme}://{self.host}:{self.port}'

    def do_request(self, method, path, body=None, headers=None):
        if not headers:
            headers = self.headers
        LOG.debug("Request: %s %s body:%s, headers:%s",
                  method, path, body, headers)
        body = json.dumps(body) if (body and isinstance(body, dict)) else body
        self.connection.connect()
        self.connection.request(method, path, body, headers)
        resp = self.connection.getresponse()
        headers = dict(resp.getheaders())
        content = resp.read()
        self.connection.close()
        resp = Response(resp.status, headers, content)
        LOG.debug("Response: %s", resp)
        if resp.status in self.ERROR_CODES:
            raise self.ERROR_CODES.get(resp.status)()
        return resp

    def get(self, path, headers=None):
        """
        :param path: the path of request
        :param headers: the header of request, type is dict
        :return: json or str
        """
        return self.do_request('GET', path, None, headers or self.headers)

    def post(self, path, body, headers=None):
        """
        :param path: the path of request
        :param body: the body of request
        :param headers: the header of request, type is dict
        :return: json or str
        """
        return self.do_request('POST', path, body, headers or self.headers)

    def put(self, path, body, headers=None):
        """
        :param path: the path of request
        :param body: the body or request
        :param headers: the headers of request, type is dict
        :return:
        """
        return self.do_request('PUT', path, body, headers or self.headers)

    def delete(self, path, headers=None):
        """
        :param path: the path of request
        :param headers: the header of request, type is dict
        :return: json or str
        """
        return self.do_request('DELETE', path, None, headers or self.headers)

    @property
    def headers(self):
        return {"Content-Type": "application/json"}
