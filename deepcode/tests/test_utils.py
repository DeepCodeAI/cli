import unittest
import os
from deepcode.src.utils.analysis_utils import hash_file_content, file_contents_as_string, hash_files

MAX_FILE_SIZE = 1000000


class TestFileHash(unittest.TestCase):
    def test_hash_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            'mocked_for_tests', 'test.java')
        sha256 = hash_file_content(
            file_contents_as_string(path, MAX_FILE_SIZE))
        self.assertEqual(
            '09f4ca64118f029e5a894305dfc329c930ebd2a258052de9e81f895b055ec929', sha256)


class TestFileUtf8Hash(unittest.TestCase):
    def test_hash_utf8_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            'mocked_for_tests', 'sample_repository/utf8.js')
        sha256 = hash_file_content(
            file_contents_as_string(path, MAX_FILE_SIZE))
        self.assertEqual(
            'cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804', sha256)


class TestFileIsoHash(unittest.TestCase):
    def test_iso8859_file(self):
        path = os.path.join(os.path.dirname(__file__),
                            'mocked_for_tests', 'sample_repository/main.js')
        sha256 = hash_file_content(
            file_contents_as_string(path, MAX_FILE_SIZE))
        self.assertEqual(
            'a7f2b4086183e471a0024b96a2de53b4a46eef78f4cf33b8dab61eae5e27eb83', sha256)


class TestHashFilesBundle(unittest.TestCase):
    def test_hash_files(self):
        mocked_files_filters = {
            'extensions': ['.java', '.html', '.js', '.jsx', '.ts', '.tsx', '.vue', '.py'],
            'configFiles': ['.pmdrc.xml', '.ruleset.xml', 'ruleset.xml', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', 'tslint.json', '.pylintrc', 'pylintrc']}

        path = os.path.join(os.path.dirname(__file__),
                            'mocked_for_tests', 'sample_repository')
        res = hash_files(path=path, max_file_size=MAX_FILE_SIZE,
                         filters_dict=mocked_files_filters, show_progressbar=False)
        self.assertEqual(3, len(res))
        res_set = set((res[item], item)for item in res)
        self.assertIn(
            ('a7f2b4086183e471a0024b96a2de53b4a46eef78f4cf33b8dab61eae5e27eb83', 'main.js'), res_set)
        self.assertIn(('c8bc645260a7d1a0d1349a72150cb65fa005188142dca30d09c3cc67c7974923',
                       'sub_folder/test2.js'), res_set)
        self.assertIn(
            ('cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804', 'utf8.js'), res_set)


if __name__ == '__main__':
    unittest.main()
