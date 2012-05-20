import time
from selenium.webdriver.support.ui import WebDriverWait

class Page(object):

    def __init__(self, browser, url = None):
        self.browser = browser
        if url: self.browser.get(url)

    def assert_title(self, expected_title):
        if self.browser.title != expected_title:
            raise AssertionError("Expected title '%s', was '%s'." % (expected_title, self.browser.title))

class WelcomePage(Page):

    url = "localhost:8080/index.html"
    
    def __init__(self, browser, get = False):
        Page.__init__(self, browser, self.url if get else None)
        self.assert_title("Chat - Welcome")

    def enter_chat(self):
        self.browser.find_element_by_id("chat-link").click()
        return ChatPage(self.browser)

    def open_popup(self):
        self.browser.find_element_by_id("popup-link").click()
        return PopupPage(self.browser)

class PopupPage(Page):

    def __init__(self, browser):
        Page.__init__(self, browser)
        self.old_window_handle = self.browser.current_window_handle
        self.browser.switch_to_window('popup')
        self.assert_title("Chat - Popup")

    def close(self):
        self.browser.find_element_by_id("close-link").click()
        self.browser.switch_to_window(self.old_window_handle)
        return WelcomePage(self.browser)
    
class ChatPage(Page):

    url = "localhost:8080/chat.html"

    def __init__(self, browser, get = False):
        Page.__init__(self, browser, self.url if get else None)
        self.assert_title("Chat - Chatroom")

    def send_chat_message(self, text):
        self.browser.find_element_by_id("text").send_keys(text)
        self.browser.find_element_by_id("send").click()

    def get_last_message(self):
        return self.browser.find_element_by_xpath("//div[@id='chat']/p[last()]").text

    def wait_for_chat_text(self, message, timeout = 2):
        try:
            WebDriverWait(self.browser, timeout, poll_frequency = 0.1)\
                .until(lambda b: message in b.find_element_by_id("chat").text)
        except TimeoutException:
            pass
        
    def get_last_message_color(self):
        style = self.browser.find_element_by_xpath("//div[@id='chat']/p[last()]").get_attribute("style")
        if "red" in style:
            return "red"
        return "black"
        
