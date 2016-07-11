# coding=utf-8
import warnings

from requests.structures import CaseInsensitiveDict

from unirio.api.result import *
from unirio.api.exceptions import *
from collections import Iterable, Sized, Mapping
from tests.request import TestAPIRequest


class TestGETRequest(TestAPIRequest):
    def test_valid_endpoint_with_permission(self):
        try:
            result = self.api.get(self.valid_endpoint)
            self.assertIsInstance(result, APIResultObject)
        except NoContentException:
            self.__no_content_warning()

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.get(path)

    def test_invalid_endpoint(self):
        for path in self.endpoints['invalid_endpoints']:
            with self.assertRaises(InvalidEndpointException):
                self.api.get(path)

    def __test_orderby(self, params, assertion):
        fields = ('PROJNAME', 'DEPTNO',)
        for field in fields:
            p = params.copy()
            p.update({'ORDERBY': field})
            result = self.api.get(self.valid_endpoint, p)
            not_null_entries = [entry for entry in result.content if entry[field]]
            for i, j in zip(not_null_entries, not_null_entries[1:]):
                assertion(i[field], j[field])

    def test_orderby_asc_without_sort(self):
        self.__test_orderby({}, self.assertLessEqual)

    def test_orderby_asc_with_sort(self):
        self.__test_orderby({'SORT': 'ASC'}, self.assertLessEqual)

    def test_orderby_desc(self):
        self.__test_orderby({'SORT': 'DESC'}, self.assertGreaterEqual)

    def test_orderby_invalid_field(self):
        with self.assertRaises(InvalidParametersException):
            self.api.get(self.valid_endpoint, {'ORDERBY': self.random_string(10)})

    def test_orderby_with_invalid_sort(self):
        with self.assertRaises(InvalidParametersException):
            self.__test_orderby({'SORT': self.random_string(6)}, None)

    def test_valid_endpoint_with_permission_and_invalid_parameters(self):
        with self.assertRaises(InvalidParametersException):
            self.api.get(
                self.valid_endpoint,
                {self.random_string(3): self.random_string(3) for i in range(0, 4)}
            )

    def test_valid_endpoint_with_permission_and_invalid_empty_parameters_value(self):
        with self.assertRaises(NullParameterException):
            result = self.api.get(
                self.valid_endpoint,
                {self.random_string(3): '' for i in range(0, 4)}
            )
            self.assertIsInstance(result, APIResultObject)

    def test_valid_endpoint_with_permission_and_invalid_list_parameters_types(self):
        with self.assertRaises(NoContentException):
            self.api.get(
                self.valid_endpoint,
                {'PROJNAME_SET': tuple(self.random_string(i) for i in range(0, 10))}
            )

    def test_valid_endpoint_with_permission_and_valid_list_parameters_types(self):
        entries = tuple(entry['PROJNAME'] for entry in self.api.get(self.valid_endpoint).content if entry['PROJNAME'])
        result = self.api.get(self.valid_endpoint, {'PROJNAME_SET': entries}).content
        self.assertEqual(set(entries), set([i['PROJNAME'] for i in result]))

    def test_first_valid_content(self):
        try:
            result = self.api.get(self.valid_endpoint).first()
            self.assertIsInstance(result, Mapping)
        except NoContentException:
            self.__no_content_warning()

    def test_first_invalid_params(self):
        for path in self.endpoints['invalid_permission'] + self.endpoints['invalid_endpoints']:
            with self.assertRaises(APIException):
                self.api.get(path).first()

    def __no_content_warning(self):
        warnings.warn("Test passed but should be run again with content on test endpoint %s" % self.valid_endpoint)

    def test_valid_endpoint_with_content_bypassing_no_content_exception(self):
        l = self.api.get(self.valid_endpoint, bypass_no_content_exception=True)
        self.assertIsInstance(l, Iterable)

    def test_valid_endpoint_without_content_bypassing_no_content_exception(self):
        l = self.api.get(
            self.valid_endpoint,
            {self.valid_endpoint_pkey: 99999999999999999999999999999},
            bypass_no_content_exception=True
        )
        self.assertIsInstance(l, Iterable)
        self.assertIsInstance(l, Sized)
        self.assertEqual(len(l), 0)

    def test_get_invalid_endpoint_bypassing_no_content_exception(self):
        with self.assertRaises(InvalidEndpointException):
            self.api.get(self.endpoints['invalid_endpoints'][0], bypass_no_content_exception=True)

    def test_get_single_result_with_content(self):
        single_result = self.api.get_single_result(self.valid_endpoint)
        self.assertIsInstance(single_result, Mapping)

    def test_get_single_result_without_content(self):
        with self.assertRaises(NoContentException):
            self.api.get_single_result(self.valid_endpoint, {self.valid_endpoint_pkey: 99999999999999999999999999999})

    def test_get_single_result_invalid_endpoint(self):
        with self.assertRaises(InvalidEndpointException):
            self.api.get_single_result(self.endpoints['invalid_endpoints'][0])

    def test_get_single_result_with_content_bypassing_no_content_exception(self):
        single_result = self.api.get_single_result(self.valid_endpoint, bypass_no_content_exception=True)
        self.assertIsInstance(single_result, Mapping)

    def test_get_single_result_without_content_bypassing_no_content_exception(self):
        single_result = self.api.get_single_result(self.valid_endpoint,
                                                   {self.valid_endpoint_pkey: 99999999999999999999999999999},
                                                   bypass_no_content_exception=True)
        self.assertEquals(single_result, None)

    def test_get_single_result_invalid_endpoint_bypassing_no_content_exception(self):
        with self.assertRaises(InvalidEndpointException):
            self.api.get_single_result(self.endpoints['invalid_endpoints'][0], bypass_no_content_exception=True)

    def test_case_insensibility(self):
        valid_entry = self.api.get_single_result(self.valid_endpoint)

        assert isinstance(valid_entry, CaseInsensitiveDict)

        def params_from_entry(str_func, entry):
            return {getattr(k, str_func)(): v for k, v in entry.items() if v and (k != 'blobcol')}

        upper_result = self.api.get_single_result(self.valid_endpoint, params_from_entry('upper', valid_entry))
        lower_result = self.api.get_single_result(self.valid_endpoint, params_from_entry('lower', valid_entry))

        assert valid_entry == upper_result == lower_result
