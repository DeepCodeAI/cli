import os.path
import pytest
import aiohttp

from deepcode.files import get_file_meta, collect_bundle_files, prepare_bundle_hashes
from deepcode.bundle import get_filters, generate_bundle, create_git_bundle
from deepcode.analysis import get_analysis
from deepcode.constants import DEFAULT_SERVICE_URL, API_KEY_ENV, SERVICE_URL_ENV
from deepcode import analyze_folders, analyze_git

MOCKED_FILTERS = {
    'extensions': [
        '.py',
        '.c',
        '.cc',
        '.cpp',
        '.cxx',
        '.h',
        '.hpp',
        '.hxx',
        '.es',
        '.es6',
        '.htm',
        '.html',
        '.js',
        '.jsx',
        '.ts',
        '.tsx',
        '.vue',
        '.java',
    ],
    'configFiles': [
        '.dcignore',
        '.gitignore',
        '.pylintrc',
        'pylintrc',
        '.pmdrc.xml',
        '.ruleset.xml',
        'ruleset.xml',
        'tslint.json',
        '.eslintrc.js',
        '.eslintrc.json',
        '.eslintrc.yml',
    ]
}

mock_file_filter = lambda n: os.path.splitext(n)[-1] in MOCKED_FILTERS['extensions'] or n in MOCKED_FILTERS['configFiles']


API_KEY = os.environ.get(API_KEY_ENV) or ''
SERVICE_URL = os.environ.get(SERVICE_URL_ENV) or DEFAULT_SERVICE_URL

# Clean environment variable
os.environ[API_KEY_ENV] = ''

def test_api_key_provided():
    assert bool(API_KEY)

@pytest.mark.asyncio
async def test_filters():

    # Call without api key and it should work
    filter_func = await get_filters(api_key=API_KEY)

    assert filter_func('sample-repo/app.js') == True


def test_meta_utf8_file():
    path = os.path.join(os.path.dirname(__file__), 'sample-repo', 'app.js')

    assert get_file_meta(path) == (510, '40f937553fda7b9986c3a87d39802b96e77fb2ba306dd602f9b2d28949316c98')


def test_meta_iso8859_file():
    path = os.path.join(os.path.dirname(__file__), 'sample-repo', 'main.js')

    assert get_file_meta(path) == (22325, 'a7f2b4086183e471a0024b96a2de53b4a46eef78f4cf33b8dab61eae5e27eb83')



def test_bundle_hashes():
    path = os.path.join(os.path.dirname(__file__), 'sample-repo')
    bundle_files = list(collect_bundle_files([path], file_filter=mock_file_filter))

    assert len(bundle_files) == 9

    file_hashes = prepare_bundle_hashes(bundle_files)

    assert len(file_hashes) == 9

    annotator_app_file = next((f for f in file_hashes if 'AnnotatorTest.cpp' in f[0]), None)
    assert 'AnnotatorTest.cpp' in annotator_app_file[0]
    assert annotator_app_file[1] == '9bf5582f88c6f5a93207efc66b3df6dd36b16de3807f93894b58baa90735b91d'

    db_file = next((f for f in file_hashes if 'db.js' in f[0]), None)
    assert 'db.js' in db_file[0]
    assert db_file[1] == '6f8d7925b5c86bd6d31b0b23bdce1dcfc94e28a1d5ebdc0ba91fac7dc7e95657'

    return file_hashes


@pytest.mark.asyncio
async def test_generate_bundle():
    """ Test generating bundles """
    file_hashes = test_bundle_hashes()

    # Try to call without api key
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):
        await generate_bundle(file_hashes)

    bundle_id = await generate_bundle(file_hashes, API_KEY)
    assert bool(bundle_id)

    return bundle_id

@pytest.mark.asyncio
async def test_analysis():

    # Try to call with wrong bundle id and without api key
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):
        await get_analysis('sdfs', linters_enabled=True)

    bundle_id = await test_generate_bundle()

    # Set API KEY env variable
    os.environ[API_KEY_ENV] = API_KEY

    results = await get_analysis(bundle_id, linters_enabled=True)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert results['id'] == bundle_id
    assert results['url'] == '{}/app/{}/_/%2F/code/?'.format(SERVICE_URL, bundle_id)
    assert list(results['results'].keys()) == ['files', 'suggestions', 'timing']
    assert len(results['results']['files'].keys()) == 5
    assert '/sample-repo/AnnotatorTest.cpp' in list(results['results']['files'].keys())[0]
    assert len(results['results']['suggestions'].keys()) == 8


@pytest.mark.asyncio
async def test_analyze_folders():
    path = os.path.join(os.path.dirname(__file__), 'sample-repo')
    results = await analyze_folders([path], linters_enabled=True)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 5
    assert len(results['results']['suggestions'].keys()) == 8


@pytest.mark.asyncio
async def test_analyze_file():
    path = os.path.join(os.path.dirname(__file__), 'sample-repo', 'app.js')
    results = await analyze_folders([path], linters_enabled=True)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 1
    assert len(results['results']['suggestions'].keys()) == 1


@pytest.mark.asyncio
async def test_analyze_folders_severity():
    path = os.path.join(os.path.dirname(__file__), 'sample-repo')
    results = await analyze_folders([path], linters_enabled=True, severity=2)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 5
    assert len(results['results']['suggestions'].keys()) == 6


@pytest.mark.asyncio
async def test_remote_analysis():
    results = await analyze_git('github.com', 'DeepcodeAI', 'TinyTests', '84b024559a6440e70faadf4d2b30609a7944f237')
    assert list(results.keys()) == ['id', 'url', 'results']
    assert set(results['results']['files'].keys()) == set(['/New.js', '/Test.java', '/Test1.java', '/Test2.java', '/Test3.java', '/Test4.java', '/Test7.java'])
    assert len(results['results']['suggestions'].keys()) == 6


@pytest.mark.asyncio
async def test_remote_analysis_severity():
    results = await analyze_git('github.com', 'DeepcodeAI', 'cli', '320d98a6896f5376efe6cefefb6e70b46b97d566', severity=2)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 0
    assert len(results['results']['suggestions'].keys()) == 0
