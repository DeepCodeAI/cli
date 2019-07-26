"""
Copyright 2019 DeepCode AG

Author: Jan Eberhardt
"""

import json
import os
import sys
import unittest
import warnings

import httpretty

from dc_analysis import DCAnalysis
from config import Config

MOCK_SESSION_TOKEN = 'abcd0123'
MOCK_BUNDLE_ID = '12345678'

API_BASE = 'http://localhost:3000/publicapi'


def init_config(c, session_token=None):
    c.data = {'dc_server_host': 'http://localhost',
              'dc_server_port': '3000'}
    if session_token:
        c.data['session_token'] = session_token


class TestDCAnalysisWithMockServer(unittest.TestCase):
    def setUp(self):
        if sys.version_info >= (3, 6):
            # https://github.com/gabrielfalcao/HTTPretty/issues/368#issuecomment-463102978
            warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*")
        self.config = Config('/tmp/test_config')
        init_config(self.config)

    def tearDown(self):
        httpretty.reset()

    @httpretty.activate
    def test_first_login(self):
        dc = DCAnalysis(self.config, silent=True)

        login_url = 'http://localhost/login'
        httpretty.register_uri(
            httpretty.POST,
            '{}/login'.format(API_BASE),
            body=json.dumps({'sessionToken': MOCK_SESSION_TOKEN,
                             'loginURL': login_url}))

        actual = dc.login()
        self.assertEqual(login_url, actual)
        self.assertIn('session_token', self.config.data)

        self.assertEqual(1, len(httpretty.HTTPretty.latest_requests))

        checklogin_request = httpretty.HTTPretty.latest_requests[0]
        expected_path = '/publicapi/login'
        self.assertEqual(expected_path, checklogin_request.path)

    @httpretty.activate
    def test_login(self):
        self.config.set_session_token(MOCK_SESSION_TOKEN)
        dc = DCAnalysis(self.config, silent=True)

        httpretty.register_uri(
            httpretty.GET,
            '{}/session'.format(API_BASE),
            status=200,
            body=json.dumps({'type': 'public'}))

        res = dc.login()

        self.assertEqual('public', res)

        self.assertEqual(1, len(httpretty.HTTPretty.latest_requests))

        checklogin_request = httpretty.HTTPretty.latest_requests[0]
        expected = {'sessionToken': [MOCK_SESSION_TOKEN]}
        self.assertEqual(expected, checklogin_request.querystring)

    def test_logout(self):
        self.config.set_session_token(MOCK_SESSION_TOKEN)
        dc = DCAnalysis(self.config, silent=True)
        dc.logout()
        self.assertNotIn('session_token', self.config.data)

    @httpretty.activate
    def test_analyze(self):
        self.config.set_session_token(MOCK_SESSION_TOKEN)
        dc = DCAnalysis(self.config, silent=True)

        httpretty.register_uri(
            httpretty.GET,
            '{}/session'.format(API_BASE),
            status=200,
            body=json.dumps({'type': 'public'}))

        httpretty.register_uri(
            httpretty.GET,
            '{}/filters'.format(API_BASE),
            status=200,
            body=json.dumps({'extensions': '.js', 'configFiles': []}))

        httpretty.register_uri(
            httpretty.POST,
            '{}/bundle'.format(API_BASE),
            status=200,
            body=json.dumps({'bundleId': MOCK_BUNDLE_ID,
                             'missingFiles': ['/sub_folder/test2.js'],
                             'uploadURL': 'http://localhost:3000/upload'}))

        httpretty.register_uri(
            httpretty.POST,
            'http://localhost:3000/upload',
            status=200)

        httpretty.register_uri(
            httpretty.GET,
            '{}/analysis/{}'.format(API_BASE, MOCK_BUNDLE_ID),
            status=200,
            body=json.dumps({'status': 'DONE',
                             'analysisResults': {
                                 'files': {'/main.js': {'0': [{'rows': [1, 2], 'cols': [3, 4]}]}},
                                 'suggestions': {
                                     '0': {'message': 'some message', 'severity': 1}}},
                             'analysisURL': 'http://deepcode.ai/something'}))

        path = os.path.join(os.path.dirname(__file__), 'test_data', 'sample_repository')
        res = dc.analyze(path)

        # suggestion is returned
        expected_suggestions = {'files': {'/main.js': {'0': [{'rows': [1, 2], 'cols': [3, 4]}]}},
                                'suggestions':
                                    {'0': {'message': 'some message', 'severity': 1}}}
        self.assertEqual(expected_suggestions, res.suggestions)

        self.assertEqual(5, len(httpretty.HTTPretty.latest_requests))

        # correct create bundle request has been made
        createbundle_request = httpretty.HTTPretty.latest_requests[2]
        expected = {'files': {'/main.js': '343166d32ee38d4aae373a88496b2d809a6c0b378dd98c96d9e3a241e13fea67',
                              '/sub_folder/test2.js': '60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752',
                              '/utf8.js': 'cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804'}}
        self.assertEqual(expected, json.loads(createbundle_request.body))
        expected = {'sessionToken': [MOCK_SESSION_TOKEN]}
        self.assertEqual(expected, createbundle_request.querystring)

        # correct upload request has been made
        upload_request = httpretty.HTTPretty.latest_requests[3]
        expected = [{'fileContent': 'test2',
                     'fileHash': '60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752'}]
        self.assertEqual(expected, json.loads(upload_request.body))
        expected = {'sessionToken': [MOCK_SESSION_TOKEN]}
        self.assertEqual(expected, upload_request.querystring)

        # correct get analysis request has been made
        analysis_request = httpretty.HTTPretty.latest_requests[4]
        expected = {'sessionToken': [MOCK_SESSION_TOKEN]}
        self.assertEqual(expected, analysis_request.querystring)


if __name__ == '__main__':
    unittest.main()
