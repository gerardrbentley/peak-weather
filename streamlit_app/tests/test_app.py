import pytest
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase


class VisualTest(BaseCase):
    @pytest.mark.e2e
    def test_app_runs(self):
        # automated visual regression testing
        # tests page has identical structure to baseline
        # https://github.com/seleniumbase/SeleniumBase/tree/master/examples/visual_testing
        self.open("http://localhost:8501")
        self.wait_for_element("#peak-weather")
        self.assert_element("#peak-weather")
        self.check_window(name="app_runs", level=2)