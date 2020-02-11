import unittest
import json
import os
import sys
import httpretty
import warnings
from deepcode.src.modules.user import DeepCodeUser
from deepcode.src.modules.http import DeepCodeHttp
from deepcode.src.modules.bundler import DeepCodeBundler
from deepcode.src.modules.analyzer import DeepCodeAnalyzer

MOCKED_API_BASE = 'http://localhost:3000'
MOCKED_API_PREFIX = 'publicapi'
MOCKED_TOKEN = 'TEST_TOKEN'
MOCKED_BUNDLE_ID = 'test_bundle_id'


class MockedConfig:
    mocked_current_config = {
        'backend_host': MOCKED_API_BASE,
        'token': 'TEST_TOKEN'
    }

    def __init__(self):
        self.current_config = MockedConfig.mocked_current_config


class DeepCodeTestModule:
    def __init__(self):
        self.http = DeepCodeHttp(MockedConfig())
        self.analyzer = DeepCodeAnalyzer(self.http)


class TestDeepcodeMainModule(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.deepcode_test_module = DeepCodeTestModule()
        super().__init__(*args, **kwargs)

    def setUp(self):
        if sys.version_info >= (3, 6):
            # https://github.com/gabrielfalcao/HTTPretty/issues/368#issuecomment-463102978
            warnings.filterwarnings(
                "ignore", category=ResourceWarning, message="unclosed.*")

    def tearDown(self):
        httpretty.reset()

    @httpretty.activate
    def test_analysis(self):
        # registering endpoints for analysis actions
        # filters route
        httpretty.register_uri(
            httpretty.GET,
            '{}/{}/filters'.format(MOCKED_API_BASE, MOCKED_API_PREFIX),
            status=200,
            body=json.dumps({'extensions': ['.js'], 'configFiles': []}))
        # create bundle
        httpretty.register_uri(
            httpretty.POST,
            '{}/{}/bundle'.format(MOCKED_API_BASE, MOCKED_API_PREFIX),
            status=200,
            body=json.dumps({'bundleId': MOCKED_BUNDLE_ID,
                             'missingFiles': ['/sub_folder/test2.js'], })
        )
        # check bundle
        httpretty.register_uri(
            httpretty.GET,
            '{}/{}/bundle/{}'.format(
                MOCKED_API_BASE, MOCKED_API_PREFIX, MOCKED_BUNDLE_ID),
            status=200,
            body=json.dumps({'bundleId': MOCKED_BUNDLE_ID})
        )

        # upload files
        httpretty.register_uri(
            httpretty.POST,
            '{}/{}/file/{}'.format(
                MOCKED_API_BASE, MOCKED_API_PREFIX, MOCKED_BUNDLE_ID),
            status=200)
        # get analysis
        httpretty.register_uri(
            httpretty.GET,
            '{}/{}/analysis/{}'.format(
                MOCKED_API_BASE, MOCKED_API_PREFIX, MOCKED_BUNDLE_ID),
            status=200,
            body=json.dumps(
                {'status': 'DONE',
                 'progress': 1.0,
                 'analysisResults': {
                     'files': {'/main.js': {'0': [{'rows': [1, 2], 'cols': [3, 4]}]}},
                     'suggestions': {
                         '0': {'message': 'some message', 'severity': 1}}},
                 'analysisURL': 'http://deepcode.ai/something'})
        )

        # path to mocked repository for analysis
        path = os.path.join(os.path.dirname(__file__),
                            'mocked_for_tests', 'sample_repository')

        # final response with analysis results
        response = self.deepcode_test_module.analyzer.analyze_files_bundle(
            path, show_progressbar=False)

        expected_response = {'files': {'/main.js': {'0': [{'rows': [1, 2], 'cols': [3, 4]}]}},
                             'suggestions':
                             {'0': {'message': 'some message', 'severity': 1}}}

        self.assertEqual(5, len(httpretty.HTTPretty.latest_requests))
        self.assertEqual(response, expected_response)
