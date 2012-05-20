import os
import sys
import unittest
import datetime
from selenium import webdriver
from multiprocessing import Process

curr_dir = os.path.dirname(__file__)

def start_browser():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("webdriver_enable_native_events", False)
    return webdriver.Firefox(firefox_profile = profile)

def kill_browser(browser):
    if not 'KB' in os.environ:
        browser.quit()
    
class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = start_browser()

    @classmethod
    def tearDownClass(cls):
        kill_browser(cls.browser)

    def tearDown(self):
        if sys.exc_info() != (None, None, None):
            directory = "/tmp/selenium-screenshots"
            if not os.path.exists(directory):
                os.mkdir(directory)
            filename = "%s/%s_%s" % \
                (directory, self.id(), datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S"))            
            self.browser.save_screenshot(filename + '.png')
            open(filename + '.html', 'w').write(self.browser.page_source.encode("utf-8"))

def run_chat_server():
    os.close(1)
    os.open("/tmp/chatserver.out", os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    os.close(2)
    os.open("/tmp/chatserver.err", os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    server = os.path.abspath(curr_dir + "/../code/chatserver.py")
    os.execlp(server, server)

class RunChatServerTestBase(TestBase):

    @classmethod
    def setUpClass(cls):
        cls.chat_server = Process(target = run_chat_server)
        cls.chat_server.start()
        TestBase.setUpClass()

    @staticmethod
    def kill_server(server):
        server.terminate()
        server.join()
        
        
    @classmethod
    def tearDownClass(cls):
        TestBase.tearDownClass()
        cls.kill_server(cls.chat_server)
