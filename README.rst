API
===

|PyPi version| |Py versions|

Python module for the API provided by the Universidade Federal do Estado
do Rio de Janeiro (UNIRIO) Please visit http://sistemas.unirio.br/api
for futher information.

Installing
----------

::

    pip install unirio-api

File Structure
--------------

.. code:: text

    api/
    ├── MANIFEST.in
    ├── README.md
    ├── README.rst
    ├── __init__.py
    ├── requirements.txt
    ├── setup.cfg
    ├── setup.py
    ├── tests
    │   ├── __init__.py
    │   ├── config.py
    │   ├── delete.py
    │   ├── get.py
    │   ├── post.py
    │   ├── procedures.py
    │   ├── put.py
    │   ├── request.py
    ├── unirio
        ├── __init__.py
        └── api
            ├── __init__.py
            ├── exceptions.py
            ├── request.py
            ├── request.pyi
            ├── result.py

Tests
-----

|Build Status| |codecov|

::

    python -m unittest -v tests

UNIRIOAPIRequest
----------------

UNIRIOAPIRequest takes 2 arguments:

-  A valid APIKey that will be used for future requests
-  An APIServer that identify the server used to perform the requests
-  An integer identifier for the server used to perform requests.
   Default: ``APIServer.LOCAL`` (Local Server)

The Methods
-----------

The public module interface for interacting with the API methods is as
follows:

.. code:: python

    def get(self, path: str, params: Dict[str:Any], fields: list, cache_time: int) -> APIResultObject:

-  path: The API endpoint to use for the request, for example 'ALUNOS'
-  params: The parameters for the request. A value of None sends the
   automatic API parameters
-  fields: The return fields for the request. A value of None is equal
   do requesting ALL the fields

.. code:: python

    def post(self, path: str, params: Dict[str:Any]) -> APIPOSTResponse:

-  path: The API endpoint to use for the request, for example 'ALUNOS'
-  params: The parameters for the request. Should contain all the
   not-null attributes.

.. code:: python

    def delete(self, path: str, params: Dict[str:int]) -> APIDELETEResponse:

-  path: The API endpoint to use for the request, for example 'ALUNOS'
-  params: The parameters for the request. Should contain the endpoint
   unique identifier. e.g.: ``{'ID_ALUNO': 235}``

.. code:: python

    def put(self, path: str, params: Dict[str:Any]) -> APIPUTResponse:

-  path: The API endpoint to use for the request, for example 'ALUNOS'
-  params: The parameters for the request. Should contain all the
   attributes that should be updated as well as the endpoint unique
   identifier.

Usage
-----

On your models, import ``UNIRIOAPIRequest`` and the enum ``APIServer``
and create an api object using your APIKey provided by
http://sistemas.unirio.br/api

.. code:: python

    from unirio.api import UNIRIOAPIRequest, APIServer

    api_key = 'afakehashusedforthisexample'
    api = UNIRIOAPIRequest(api_key, APIServer.PRODUCTION)

Optional parameters are ``debug: boolean`` and ``cache``. ``debug``
gives console verbosity and ``cache`` is used for caching in
``UNIRIOAPIRequest.get`` method.

get
~~~

.. code:: python

    path = 'ALUNOS'
    params = {
        'LMIN' : 0,
        'LMAX' : 1000,
        'SEXO' : 'F'
        'ETNIA_ITEM' : 1
    }
    fields = ['ID_ALUNO', 'ID_PESSOA', 'SEXO']
    result = api.get(path, params, fields)  # type: unirio.api.result.APIRestultObject

The get method also have an optional parameter ``cache_time``,
representing the cache expiration time in seconds, and defaults to
``0``, that means that no cache is applied.

.. code:: python

    [...] 
    result = api.get(path, params, fields, cache_time=60)

The above request gives the same response object, but is cached for 60
seconds, wich means that if another request is made within 60 seconds,
for the same ``path``, another HTTP request wont be made to the API
server.

    **All the caching is done on the client side**, wich means that
    every request done to the api will always reflect the current state
    of the resource at the time of the request. Whenever possible, it's
    always recommended that you cache your requests, since in most cases
    it's much faster.

A method call to ``UNIRIOAPIRequest.get`` will return an
``APIResultObject`` wich is a model object and have the following
attributes:

-  ``content: list``: A list of dictionaries with the result of the GET
   request. If ``fields != None`` the dictionaries of the list will only
   contain the keys from the ``fields`` list.
-  ``lmin: int``: The offset of the request result
-  ``lmax: int``: The limit of the request result
-  ``fields: tuple``: The list of endpoint fields that should be
   returned

Exceptions
^^^^^^^^^^

-  ``NoContentException``: Raised when the api returns a 'content not
   found' status code, and it means that no content was found for the
   given parameters.

-  

post
~~~~

.. code:: python

    path = 'ALUNOS'
    params = {
        'SEXO': 'F',
        'ETNIA_ITEM': 1,
        'NOME_PAI': 'Jonathan Kent',
        'NOME_MAE': 'Martha Kent'
        'ID_PESSOA': 345
    }
    result = api.post(path, params) # type: unirio.api.result.APIPOSTResponse

A method call to ``UNIRIOAPIRequest.post`` will return an
``APIPOSTResponse`` wich is a model object and have the following
attributes:

-  ``insertId: int``: Unique identifier created on the POST request.

Exceptions
^^^^^^^^^^

-  ``InvalidParametersException``:
-  ``ContentNotCreated``:

-  

put
~~~

.. code:: python

    path = 'PESSOAS'
    params = {
        'ID_PESSOA': 345,
        'NOME_PESSOA': 'My new name'
    }
    result = api.put(path, params)  # type: unirio.api.result.APIPUTResponse

A method call to ``UNIRIOAPIRequest.put`` will return an
``APIPUTResponse`` wich is a model object and have the following
attributes:

-  ``affectedRows: int``: The number of rows affected by the PUT
   request.

Exceptions
^^^^^^^^^^

-  ``ContentNotFoundException``: Invalid unique identifier and nothing
   was updated
-  ``InvalidParametersException``: One or more of the parameters has an
   incompatible type
-  ``NothingToUpdateException``: No valid content passed on ``params``
   and nothing was updated
-  ``MissingPrimaryKeyException``: The unique identifier field isn't a
   Key in the ``params`` dictionary.

delete
~~~~~~

.. code:: python

    path = 'PESSOAS'
    params = {'ID_PESSOA': 345}
    result = api.delete(path, params)   # type: unirio.api.result.APIDELETEResponse

A method call to ``UNIRIOAPIRequest.delete`` will return an
``APIDELETEResponse`` wich is a model object and have the following
attributes:

-  ``affectedRows: int``: The number of rows affected by the DELETE
   request.

Exceptions
^^^^^^^^^^

-  ``ContentNotFoundException``: Invalid unique identifier and nothing
   was updated
-  ``NothingToUpdateException``:
-  ``MissingPrimaryKeyException``: The unique identifier field isn't a
   Key in the ``params`` dictionary.

Common Exceptions
~~~~~~~~~~~~~~~~~

-  ``ForbiddenEndpointException``: The API Key doens't have permission
   to perform the request on the ``path`` endpoint
-  ``InvalidAPIKeyException``: The API Key used is invalid or inactive
-  ``UnhandledAPIException``: Something unexpected happened on the
   server side
-  ``InvalidEndpointException``: The endpoint ``path`` doesn't exist.
   Check the list of endpoint on the main page of
   http://sistemas.unirio.br/api
-  ``InvalidParametersException``: The request was performed with
   invalid ``params`` and shouldn't be repeated used the same
   ``params``. That exception object has an ``invalid_parameters``
   attribute, wich is a list of the invalid keys on ``params``
   dictionary.

Cache
-----

Todo: Should explain the necessary interface that the cache object
should have to comply with the api cache duck typing, as well as its
usage

-  For default value references, check the API documentation.

.. |PyPi version| image:: https://img.shields.io/pypi/v/unirio-api.svg
.. |Py versions| image:: https://img.shields.io/pypi/pyversions/unirio-api.svg
.. |Build Status| image:: https://img.shields.io/travis/unirio-dtic/api_client/master.svg?style=flat-square&label=Travis-CI
   :target: https://travis-ci.org/unirio-dtic/api_client
.. |codecov| image:: https://codecov.io/gh/unirio-dtic/api_client/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/unirio-dtic/api_client
