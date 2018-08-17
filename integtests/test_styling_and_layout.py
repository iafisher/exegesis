from .base import BaseTest


class StyleLayoutTest(BaseTest):
    def test_styling_and_layout(self):
        self.log_myself_in()
        self.browser.get(self.live_server_url)

        # Make sure that the main container is centered.
        self.browser.set_window_size(1024, 768)
        div = self.browser.find_element_by_class_name('container')
        self.assertAlmostEqual(
            div.location['x'] + div.size['width'] / 2,
            512,
            delta=10
        )
