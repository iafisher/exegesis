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

        # Wait for authentication and redirection to main page.
        time.sleep(0.5)

        # Enter the information for a GitHub repo.
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys('iafisher')
        
        repo_input = self.browser.find_element_by_id('id_reponame')
        repo_input.send_keys('writingstreak')

        sha_input = self.browser.find_element_by_id('id_sha')
        sha_input.send_keys('e8101b81318b644e2b2b2cbb60e11c17433ee6c4')

        ret = self.browser.find_element_by_id('importButton').click()

        # Wait for the server to import the project.
        time.sleep(1)

        # Make sure the project was imported successfully.
        msg = self.browser.find_element_by_id('message-1')
        self.assertEqual(msg.text, 'Project imported successfully.')

        # Visit the project index.
        self.browser.get(URL + 'project/iafisher:writingstreak')

        dlist = self.browser.find_element_by_id('directory-list')
        anchors = dlist.find_elements_by_tag_name('a')

        self.assertEqual(len(anchors), 9)

        anchors_text = [a.text for a in anchors]
        self.assertIn('api', anchors_text)
        self.assertIn('compose', anchors_text)
        self.assertIn('frontend', anchors_text)
        self.assertIn('writingstreak', anchors_text)
        self.assertIn('.gitignore', anchors_text)
        self.assertIn('LICENSE', anchors_text)
        self.assertIn('README.txt', anchors_text)
        self.assertIn('manage.py', anchors_text)
        self.assertIn('requirements.txt', anchors_text)

        # Visit a folder.
        self.browser.get(URL + 'project/iafisher:writingstreak/api')

        dlist = self.browser.find_element_by_id('directory-list')
        anchors = dlist.find_elements_by_tag_name('a')

        self.assertEqual(len(anchors), 5)

        anchors_text = [a.text for a in anchors]
        self.assertIn('__init__.py', anchors_text)
        self.assertIn('apps.py', anchors_text)
        self.assertIn('tests.py', anchors_text)
        self.assertIn('urls.py', anchors_text)
        self.assertIn('views.py', anchors_text)


if __name__ == '__main__':
    unittest.main()
