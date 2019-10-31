# """
# Copyright 2019 DeepCode AG

# Author: Jan Eberhardt
# """

# import os
# import unittest

# import util

# MAX_FILE_SIZE = 1000000


# class TestFileHash(unittest.TestCase):
#     def test_hash_file(self):
#         path = os.path.join(os.path.dirname(__file__), 'test_data', 'test.java')
#         sha256 = util.hash_file_content(util.file_contents_as_string(path, MAX_FILE_SIZE))
#         self.assertEqual('09f4ca64118f029e5a894305dfc329c930ebd2a258052de9e81f895b055ec929', sha256)

#     def test_hash_utf8_file(self):
#         path = os.path.join(os.path.dirname(__file__), 'test_data', 'sample_repository/utf8.js')
#         sha256 = util.hash_file_content(util.file_contents_as_string(path, MAX_FILE_SIZE))
#         self.assertEqual('cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804', sha256)

#     def test_iso8859_file(self):
#         path = os.path.join(os.path.dirname(__file__), 'test_data', 'sample_repository/main.js')
#         sha256 = util.hash_file_content(util.file_contents_as_string(path, MAX_FILE_SIZE))
#         self.assertEqual('343166d32ee38d4aae373a88496b2d809a6c0b378dd98c96d9e3a241e13fea67', sha256)

#     def test_hash_files(self):
#         path = os.path.join(os.path.dirname(__file__), 'test_data', 'sample_repository')
#         res = util.hash_files(path, MAX_FILE_SIZE)
#         self.assertEqual(4, len(res))
#         res_set = set(res)
#         self.assertIn(('343166d32ee38d4aae373a88496b2d809a6c0b378dd98c96d9e3a241e13fea67', 'main.js'), res_set)
#         self.assertIn(('1b4f0e9851971998e732078544c96b36c3d01cedf7caa332359d6f1d83567014', 'test1.txt'), res_set)
#         self.assertIn(('60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752', 'sub_folder/test2.js'), res_set)
#         self.assertIn(('cc2b67993e547813db67f57c6b20bff83bf4ade64ea2c3fb468d927425502804', 'utf8.js'), res_set)


# if __name__ == '__main__':
#     unittest.main()
