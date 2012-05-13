import unittest
from selenium import webdriver

class BasicSeleniumTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
        
    def test_some_commands(self):
        self.browser.get("http://www.altavista.com")
        self.browser.find_element_by_id("yschsp").send_keys("sruftrain")
        self.browser.find_element_by_id("yschbt").click()
        main_text = self.browser.find_element_by_id("main").text
        self.assertTrue("Socialize the web!" in main_text)
        
if __name__ == '__main__':
    unittest.main()
        

        
