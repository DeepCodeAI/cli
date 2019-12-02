import unittest
import requests
import json
import os
from unittest import TestCase, mock
from deepcode.src.modules.user import DeepCodeUser
from deepcode.src.modules.http import DeepCodeHttp
from deepcode.src.modules.bundler import DeepCodeBundler
from deepcode.src.modules.analyzer import DeepCodeAnalyzer


MOCKED_BACKEND_HOST = 'https://test_backend_host'
MOCKED_TOKEN = 'TEST_TOKEN'

login_response = {'sessionToken': MOCKED_TOKEN, 'loginURL': 'test_login_URL'}
check_login_response = ''
filters_response = {'extensions': [], 'configFiles': []}
bundle_response = {
    'bundleId': 'test_bundle_id',
    'missingFiles': ['/sub_folder/test2.js'],
    'uploadURL': 'test_uplaod_url',
}
analysis_response = {
    'status': 'DONE',
    'progress': 1,
    'analysisURL': 'test_analysis_url',
    'analysisResults': {
        'files': {'/main.js': {'0': [{'rows': [1, 2], 'cols': [3, 4]}]}},
        'suggestions': {'0': {'message': 'some message', 'severity': 1}}
    }
}

api_test_routes_and_responses = {
    '{}/publicapi/login'.format(MOCKED_BACKEND_HOST): login_response,
    '{}/publicapi/session'.format(MOCKED_BACKEND_HOST): check_login_response,
    '{}/publicapi/filters'.format(MOCKED_BACKEND_HOST): filters_response,
    '{}/publicapi/bundle'.format(MOCKED_BACKEND_HOST): bundle_response,
    '{}/publicapi/bundle/test_bundle_id'.format(MOCKED_BACKEND_HOST): bundle_response,
    '{}/publicapi/analysis/test_bundle_id'.format(MOCKED_BACKEND_HOST): analysis_response,
    '{}/publicapi/analysis/test_base_bundle_id/test_target_bundle_id'.format(MOCKED_BACKEND_HOST): analysis_response
}


class MockedResponse:
    def __init__(self, response_data, status_code):
        self.response_data = response_data
        self.status_code = status_code

    def json(self):
        return self.response_data

    def content(self):
        return self.response_data


def response_side_effect(*args, **kwargs):
    called_edpoint = args[0]
    if called_edpoint in api_test_routes_and_responses:
        return MockedResponse(api_test_routes_and_responses[called_edpoint], 200)
    return MockedResponse(None, 404)


class MockedConfig:
    def __init__(self):
        self.current_config = {
            'BACKEND_HOST': MOCKED_BACKEND_HOST,
            'TOKEN': MOCKED_TOKEN,
        }


class DeepCodeTestModule:
    def __init__(self):
        self.http = DeepCodeHttp(MockedConfig())
        self.user = DeepCodeUser(self.http)
        self.bundler = DeepCodeBundler(self.http)
        self.analyzer = DeepCodeAnalyzer(self.http)


class TestHttp(TestCase):

    def __init__(self, *args, **kwargs):
        self.deepcode_test_module = DeepCodeTestModule()
        super().__init__(*args, **kwargs)

    @mock.patch('requests.post', side_effect=response_side_effect)
    def test_login(self, mock_object):
        response_data = self.deepcode_test_module.user.login()
        self.assertEqual(response_data, login_response)

    @mock.patch('requests.get', side_effect=response_side_effect)
    def test_check_login(self, mock_object):
        response_data = self.deepcode_test_module.user.check_login(
            token='TEST_TOKEN')
        self.assertEqual(response_data, True)

    @mock.patch('requests.get', side_effect=response_side_effect)
    def test_get_filters(self, mocked_response):
        response_data = self.deepcode_test_module.bundler.create_files_filters_from_server()
        self.assertEqual(response_data, filters_response)

    @mock.patch('requests.post', side_effect=response_side_effect)
    def test_create_server_bundle(self, mocked_response):
        response_data = self.deepcode_test_module.bundler.create_files_server_bundle(
            [{'file1path': 'file1hash', 'file2path': 'file2hash'}])
        self.assertEqual(response_data, bundle_response)

    @mock.patch('requests.get', side_effect=response_side_effect)
    def test_check_server_bundle(self, mocked_response):
        response_data = self.deepcode_test_module.bundler.check_server_bundle_on_server(
            'test_bundle_id')
        self.assertEqual(response_data, bundle_response)

    @mock.patch('requests.get', side_effect=response_side_effect)
    def test_get_analysis(self, mocked_response):
        response_data = self.deepcode_test_module.analyzer.analyze(
            'test_bundle_id', show_progressbar=False)
        self.assertEqual(response_data, analysis_response['analysisResults'])

    @mock.patch('requests.get', side_effect=response_side_effect)
    def test_get_diff_analysis(self, mocked_response):
        response_data = self.deepcode_test_module.analyzer.analyze(
            'test_base_bundle_id/test_target_bundle_id', show_progressbar=False)
        self.assertEqual(response_data, analysis_response['analysisResults'])


if __name__ == '__main__':
    unittest.main()
