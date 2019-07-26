"""
Copyright 2019 DeepCode AG

Author: Jan Eberhardt
"""

import time
from collections import namedtuple

import requests
from requests_futures.sessions import FuturesSession

POLLING_INTERVAL = 1  # in seconds
MAX_NUM_POLLS = 3600
MAX_PARALLEL_REQUESTS = 10
ENDPOINTS_PREFIX = 'publicapi'

LoginResponse = namedtuple('LoginResponse', 'login_url')
CheckLoginResponse = namedtuple('CheckLoginResponse', 'type')
CreateBundleFromRepoResponse = namedtuple('CreateBundleFromRepoResponse', 'bundle_id')
GetFiltersResponse = namedtuple('GetFiltersResponse', 'extensions config_files')
CreateBundleFromFilesResponse = namedtuple('CreateBundleFromFilesResponse',
                                           'bundle_id upload_url missing_files')
GetAnalysisResponse = namedtuple('GetAnalysisResponse', 'status suggestions url')
GetSuggestionResponse = namedtuple('GetSuggestionsResponse', 'suggestions')


class ApiException(Exception):
    pass


class ApiUnauthorizedException(ApiException):
    pass


class ApiRequestBodyTooLarge(ApiException):
    pass


class JobBundles:
    def __init__(self, bundle_id1, bundle_id2=None):
        self.bundle_id1 = bundle_id1
        self.bundle_id2 = bundle_id2

    def to_endpoint(self):
        if self.bundle_id2:
            return '{}/{}'.format(self.bundle_id1, self.bundle_id2)
        else:
            return '{}'.format(self.bundle_id1)


def code_to_message(code):
    if code in requests.status_codes._codes:
        return requests.status_codes._codes[code][0]
    else:
        return '_'


def create_api_exception_from(err):
    if isinstance(err, ApiException):
        return err
    elif isinstance(err, requests.exceptions.ConnectionError):
        return ApiException('Connection refused')
    elif isinstance(err, requests.exceptions.RequestException):
        return ApiException('Request exception')
    else:
        return ApiException('Unexpected error')


def check_response_has(response, keys):
    for key in keys:
        if key not in response:
            raise ApiException('Expected server response to contain {}.'.format(key))


class Api:
    def __init__(self, config):
        self.dc_server_host = config.data['dc_server_host']
        self.dc_server_port = config.data['dc_server_port']
        self.config = config
        self.session_token = config.data.get('session_token', None)
        self.base_endpoint = '{}:{}/{}'.format(self.dc_server_host,
                                               self.dc_server_port,
                                               ENDPOINTS_PREFIX)

    def login(self):
        try:
            res = requests.post('{}/login'.format(self.base_endpoint))
            if res.status_code == requests.codes.ok:
                data = res.json()
                check_response_has(data, ['sessionToken', 'loginURL'])
                self._set_session_token(data['sessionToken'])
                return LoginResponse(data['loginURL'])
            else:
                raise ApiException('Server response code: {}'.format(res.status_code))
        except Exception as err:
            raise create_api_exception_from(err)

    def _set_session_token(self, session_token):
        self.config.set_session_token(session_token)
        self.session_token = session_token

    def check_login(self):
        if not self.session_token:
            return CheckLoginResponse(None)
        try:
            params = {'sessionToken': self.session_token}
            res = requests.get('{}/session'.format(self.base_endpoint), params=params)
            if res.status_code == requests.codes.ok:
                data = res.json()
                check_response_has(data, ['type'])
                return CheckLoginResponse(data['type'])
            elif res.status_code == requests.codes.unauthorized \
                    or res.status_code == requests.codes.not_modified:
                return CheckLoginResponse(None)
            else:
                raise ApiException('Server response code: {}'.format(res.status_code))
        except Exception as err:
            raise create_api_exception_from(err)

    def wait_for_login(self):
        try:
            res = self.check_login()
            for _ in range(MAX_NUM_POLLS):
                if res.type:
                    return res
                time.sleep(POLLING_INTERVAL)
                res = self.check_login()
        except Exception as err:
            raise create_api_exception_from(err)
        raise ApiException('Timeout while waiting for login')

    def get_filters(self):
        try:
            params = {'sessionToken': self.session_token}
            res_data = requests.get('{}/filters'.format(self.base_endpoint), params=params).json()
            extensions = res_data['extensions']
            config_files = list(map(lambda cf: self.canonicalize_path(cf),
                                    res_data['configFiles']))
            return GetFiltersResponse(extensions, config_files)
        except Exception as err:
            raise create_api_exception_from(err)

    def create_bundle_from_repo(self, owner, repo, oid):
        try:
            payload = {'owner': owner, 'repo': repo}
            if oid:
                payload['oid'] = oid
            res_data = self._create_bundle_with_payload(payload)
            check_response_has(res_data, ['bundleId'])
            return CreateBundleFromRepoResponse(res_data['bundleId'])
        except Exception as err:
            raise create_api_exception_from(err)

    def create_bundle_from_files(self, bundle):
        bundle_dict = bundle.to_dict()
        uncanonical_bundle_dict = {}
        for path, file_hash in bundle_dict.items():
            canonical_path = self.reverse_canonicalize_path(path)
            uncanonical_bundle_dict[canonical_path] = file_hash
        payload = {'files': uncanonical_bundle_dict}
        try:
            res_data = self._create_bundle_with_payload(payload)
            check_response_has(res_data, ['missingFiles', 'bundleId', 'uploadURL'])
            missing_files = list(map(lambda m: self.canonicalize_path(m),
                                     res_data['missingFiles']))
            return CreateBundleFromFilesResponse(res_data['bundleId'],
                                                 res_data['uploadURL'],
                                                 missing_files)
        except Exception as err:
            raise create_api_exception_from(err)

    def _create_bundle_with_payload(self, payload):
        params = {'sessionToken': self.session_token}
        res = requests.post('{}/bundle'.format(self.base_endpoint), json=payload, params=params)
        if res.status_code == requests.codes.ok:
            data = res.json()
            return data
        elif res.status_code == requests.codes.unauthorized:
            raise ApiUnauthorizedException()
        elif res.status_code == requests.codes.request_entity_too_large:
            raise ApiRequestBodyTooLarge()
        else:
            raise ApiException('Server response code: {}'.format(res.status_code))

    def upload_batches(self, url, batches, progress_iterator):
        def handle_batch(session, batch):
            payload = []
            for file_content, file_hash in batch:
                payload.append({'fileContent': file_content,
                                'fileHash': file_hash})
            params = {'sessionToken': self.session_token}
            # not setting the charset to utf-8 in the header leads to the server using a different encoding for
            # the file_content, the result is that a different hash is calculated in the server than what was
            # calculated in this client
            headers = {'Content-type': 'application/json; charset=utf-8'}
            return session.post(url, json=payload, params=params, headers=headers)

        try:
            with FuturesSession(max_workers=MAX_PARALLEL_REQUESTS) as futures_session:
                futures = list(map(lambda b: handle_batch(futures_session, b), batches))
                for future in progress_iterator(futures):
                    res = future.result()
                    if res.status_code == requests.codes.ok:
                        continue
                    elif res.status_code == requests.codes.unauthorized or res.status_code == requests.codes.forbidden:
                        raise ApiUnauthorizedException()
                    else:
                        code = res.status_code
                        desc = code_to_message(code)
                        raise ApiException('Server response code: {} ({})'.format(code, desc))
        except Exception as err:
            raise create_api_exception_from(err)

    def get_analysis(self, bundles, previous_status=None):
        try:
            if previous_status:
                params = {'sessionToken': self.session_token, 'status': previous_status}
            else:
                params = {'sessionToken': self.session_token}
            url = '{}/analysis/{}'.format(self.base_endpoint, bundles.to_endpoint())
            res = requests.get(url, params)
            if res.status_code == requests.codes.ok:
                data = res.json()
                check_response_has(data, ['analysisResults', 'analysisURL'])
                suggestions = data['analysisResults']
                url = data['analysisURL']
                return GetAnalysisResponse(data['status'], suggestions, url)
            elif res.status_code == requests.codes.unauthorized:
                raise ApiUnauthorizedException()
            else:
                raise ApiException('Server response code: {}'.format(res.status_code))
        except Exception as err:
            raise create_api_exception_from(err)

    def wait_for_analysis_state(self, bundles, analysis_state):
        res = self.get_analysis(bundles)
        for _ in range(MAX_NUM_POLLS):
            if res.status == analysis_state:
                return res
            elif res.status == 'FAIL':
                raise ApiException('Analysis failed')
            time.sleep(POLLING_INTERVAL)
            res = self.get_analysis(bundles, res.status)
        raise ApiException('Timeout while waiting for analysis state "{}"'.format(analysis_state))

    @staticmethod
    def canonicalize_path(path):
        """
        Remove '/' at beginning of path
        Paths that we get from the API are prefixed with '/' but are relative
        with respect to a project or repo.
        Here we strip aways that leading '/' to make the path a proper
        relative path that we can use in the file system
        """
        if path.startswith('/'):
            return path[1:]
        return path

    @staticmethod
    def reverse_canonicalize_path(path):
        """
        Prepend paths with '/'
        Reverse transformation of canonicalize_path
        """
        return '/{}'.format(path)
