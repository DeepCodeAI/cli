import os.path
import pytest
import aiohttp

from deepcode.files import get_file_meta, collect_bundle_files, prepare_bundle_hashes
from deepcode.bundle import get_filters, generate_bundle, create_git_bundle
from deepcode.analysis import get_analysis
from deepcode.constants import API_KEY_ENV, DEFAULT_SERVICE_URL
from deepcode import analyze_folders, analyze_git

MOCKED_FILTERS = {
    'extensions': ['.java', '.html', '.js', '.jsx', '.ts', '.tsx', '.vue', '.py'],
    'configFiles': ['.pmdrc.xml', '.ruleset.xml', 'ruleset.xml', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', 'tslint.json', '.pylintrc', 'pylintrc']
    }

mock_file_filter = lambda n: os.path.splitext(n)[-1] in MOCKED_FILTERS['extensions'] or n in MOCKED_FILTERS['configFiles']


API_KEY = '3f0c8e2f05b1465de310e4d7b3d80db7ee87bcf73225b6b3db97848b1d17784c'


@pytest.mark.asyncio
async def test_filters():

    # Try to call without api key
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):
        await get_filters()

    filter_func = await get_filters(api_key=API_KEY)

    assert filter_func('sample_repository/utf8.js') == True


def test_file_meta():
    path = os.path.join(os.path.dirname(__file__),
                        'mocked_for_tests', 'test.java')

    assert get_file_meta(path) == (140375, '09f4ca64118f029e5a894305dfc329c930ebd2a258052de9e81f895b055ec929')


def test_meta_utf8_file():
    path = os.path.join(os.path.dirname(__file__),
                        'mocked_for_tests', 'sample_repository/utf8.js')

    assert get_file_meta(path) == (328, 'cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804')


def test_meta_iso8859_file():
    path = os.path.join(os.path.dirname(__file__),
                        'mocked_for_tests', 'sample_repository/main.js')

    assert get_file_meta(path) == (22325, 'a7f2b4086183e471a0024b96a2de53b4a46eef78f4cf33b8dab61eae5e27eb83')



def test_bundle_hashes():
    path = os.path.join(os.path.dirname(__file__),
                        'mocked_for_tests', 'sample_repository')
    bundle_files = list(collect_bundle_files([path], file_filter=mock_file_filter))

    assert len(bundle_files) == 3

    file_hashes = prepare_bundle_hashes(bundle_files)

    assert len(file_hashes) == 3
    assert file_hashes[0][1] == 'cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804' \
           and 'utf8.js' in file_hashes[0][0]
    assert file_hashes[1][1] == 'a7f2b4086183e471a0024b96a2de53b4a46eef78f4cf33b8dab61eae5e27eb83' \
           and 'main.js' in file_hashes[1][0]
    assert file_hashes[2][1] == 'c8bc645260a7d1a0d1349a72150cb65fa005188142dca30d09c3cc67c7974923' \
           and 'sub_folder/test2.js' in file_hashes[2][0]

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
    assert results['url'] == '{}/app/{}/_/%2F/code/'.format(DEFAULT_SERVICE_URL, bundle_id)
    assert list(results['results'].keys()) == ['files', 'suggestions']
    assert len(results['results']['files'].keys()) == 1
    assert '/mocked_for_tests/sample_repository/main.js' in list(results['results']['files'].keys())[0]
    assert len(results['results']['suggestions'].keys()) == 9


@pytest.mark.asyncio
async def test_analyze_folders():
    path = os.path.join(os.path.dirname(__file__), 'mocked_for_tests')
    results = await analyze_folders([path], linters_enabled=True)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 1
    assert len(results['results']['suggestions'].keys()) == 9


@pytest.mark.asyncio
async def test_analyze_folders_severity():
    path = os.path.join(os.path.dirname(__file__), 'mocked_for_tests')
    results = await analyze_folders([path], linters_enabled=True, severity=2)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 0
    assert len(results['results']['suggestions'].keys()) == 0


@pytest.mark.asyncio
async def test_remote_analysis():
    results = await analyze_git('github.com', 'DeepcodeAI', 'cli', '320d98a6896f5376efe6cefefb6e70b46b97d566')
    assert list(results.keys()) == ['id', 'url', 'results']
    assert list(results['results']['files'].keys()) == ['/tests/mocked_for_tests/sample_repository/main.js']
    assert len(results['results']['suggestions'].keys()) == 9


@pytest.mark.asyncio
async def test_remote_analysis_severity():
    results = await analyze_git('github.com', 'DeepcodeAI', 'cli', '320d98a6896f5376efe6cefefb6e70b46b97d566', severity=2)
    assert list(results.keys()) == ['id', 'url', 'results']
    assert len(results['results']['files'].keys()) == 0
    assert len(results['results']['suggestions'].keys()) == 0
