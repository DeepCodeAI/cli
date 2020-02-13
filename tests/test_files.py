import os.path

from deepcode.files import get_file_meta, collect_bundle_files, prepare_bundle_hashes

MOCKED_FILTERS = {
    'extensions': ['.java', '.html', '.js', '.jsx', '.ts', '.tsx', '.vue', '.py'],
    'configFiles': ['.pmdrc.xml', '.ruleset.xml', 'ruleset.xml', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', 'tslint.json', '.pylintrc', 'pylintrc']
    }

mock_file_filter = lambda n: os.path.splitext(n)[-1] in MOCKED_FILTERS['extensions'] or n in MOCKED_FILTERS['configFiles']

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
