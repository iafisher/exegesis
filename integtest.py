"""An integration test for the Exegesis site.

A couple of things need to be done before running this test:

    1. Make sure that a user with the credentials TEST_USERNAME, TEST_PASSWORD
       exists.
    2. Make sure that the project 'iafisher:writingstreak' does NOT exist.
"""
from selenium import webdriver
import time
import unittest


TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'Temporary'
URL = 'http://localhost:8000/'


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_import_repo(self):
        # Log in to the site.
        self.browser.get(URL + 'login')
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys(TEST_USERNAME)
        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys(TEST_PASSWORD)

        self.browser.find_element_by_id('submit').click()

        time.sleep(0.5)

        # Load up the main page.
        self.browser.get(URL)

        # Enter the information for a GitHub repo.
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys('iafisher')
        
        repo_input = self.browser.find_element_by_id('id_reponame')
        repo_input.send_keys('writingstreak')

        sha_input = self.browser.find_element_by_id('id_sha')
        sha_input.send_keys('e8101b81318b644e2b2b2cbb60e11c17433ee6c4')

        #self.browser.find_element_by_id('importButton').click()

        # Wait for the server to import the project.
        time.sleep(1)

        # Visit the project index.
        self.browser.get(URL + 'project/iafisher:writingstreak')

        dlist = self.browser.find_element_by_id('directory-list')
        anchors = dlist.find_elements_by_tag_name('a')

        self.assertEqual(len(anchors), 9)

        self.assertTrue(any(a.text == 'api' for a in anchors))
        self.assertTrue(any(a.text == 'compose' for a in anchors))
        self.assertTrue(any(a.text == 'frontend' for a in anchors))
        self.assertTrue(any(a.text == 'writingstreak' for a in anchors))
        self.assertTrue(any(a.text == '.gitignore' for a in anchors))
        self.assertTrue(any(a.text == 'LICENSE' for a in anchors))
        self.assertTrue(any(a.text == 'README.txt' for a in anchors))
        self.assertTrue(any(a.text == 'manage.py' for a in anchors))
        self.assertTrue(any(a.text == 'requirements.txt' for a in anchors))

        # Visit a folder.
        self.browser.get(URL + 'project/iafisher:writingstreak/api')

        dlist = self.browser.find_element_by_id('directory-list')
        anchors = dlist.find_elements_by_tag_name('a')

        self.assertEqual(len(anchors), 5)

        self.assertTrue(any(a.text == '__init__.py' for a in anchors))
        self.assertTrue(any(a.text == 'apps.py' for a in anchors))
        self.assertTrue(any(a.text == 'tests.py' for a in anchors))
        self.assertTrue(any(a.text == 'urls.py' for a in anchors))
        self.assertTrue(any(a.text == 'views.py' for a in anchors))


if __name__ == '__main__':
    unittest.main()
