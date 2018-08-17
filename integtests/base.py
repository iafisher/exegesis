"""
Author:  Ian Fisher (iafisher@protonmail.com)
Version: August 2018
"""
import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'Temporary'

MAX_WAIT = 10


class BaseTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        User = get_user_model()
        User.objects.create_user(TEST_USERNAME, 'temporary@gmail.com',
            TEST_PASSWORD)

    def tearDown(self):
        self.browser.quit()

    def log_myself_in(self):
        self.browser.get(self.live_server_url + '/login')
        username_input = self.browser.find_element_by_id('id_username')
        username_input.send_keys(TEST_USERNAME)
        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys(TEST_PASSWORD)

        self.browser.find_element_by_id('submit').click()
        #self.wait_for_index_page_load()
        self.wait_for(lambda browser: 'Login' not in browser.title)

    def wait_for(self, cond, *excs):
        start_time = time.time()
        while True:
            try:
                res = cond(self.browser)
            except excs:
                pass
            else:
                if res is True:
                    break

            if time.time() - start_time > MAX_WAIT:
                raise Exception('Did not load index page quickly enough')
            time.sleep(0.1)
