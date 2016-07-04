# coding=utf-8
from unirio.api.exceptions import *
from unirio.api.result import *
from tests.request import TestAPIRequest


class TestPUTRequest(TestAPIRequest):
    @property
    def __valid_entry(self):
        """
        :rtype : dict
        """
        return self.api.get_single_result(self.valid_endpoint)

    def test_valid_endpoint_without_primary_key(self):
        PROJNAME = self._random_string(3)
        with self.assertRaises(MissingRequiredParameterException):
            self.api.put(self.valid_endpoint, {'PROJNAME': PROJNAME})

    def test_valid_endpoint_with_permission(self):
        projname = self._random_string(3)
        params = {
            self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey],
            'projname': projname
        }
        params.update(self._operador_mock)
        result = self.api.put(self.valid_endpoint, params)

        # Updated correcly with the right output ?
        self.assertIsInstance(result, APIPUTResponse)

        updated_entry = self.api.get_single_result(
            self.valid_endpoint,
            {self.valid_endpoint_pkey: self.__valid_entry[self.valid_endpoint_pkey]}
        )

        # Lets get it again and check if its the result is as expected
        self.assertEqual(updated_entry['projname'], projname)

    def test_valid_endpoint_without_permission(self):
        for path in self.endpoints['invalid_permission']:
            with self.assertRaises(ForbiddenEndpointException):
                self.api.put(path, self._invalid_dummy_params())

    # def test_valid_endpoint_with_valid_permission_and_invalid_parameters_types(self):
    #     entry = self.__valid_entry
    #     entry.update({'PRSTDATE': self._random_string(50000)})
    #     with self.assertRaises(InvalidParametersException):
    #         self.api.put(self.valid_endpoint, entry)
    #         # todo: ë necessário criar um campo não-string para esse teste