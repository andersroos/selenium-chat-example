import base
import pages

class OneBrowserTest(base.RunChatServerTestBase):

    def test_chat_with_myself(self):
        page = pages.WelcomePage(self.browser, get = True)
        page = page.enter_chat()
        page.send_chat_message("message1")
        page.wait_for_chat_text("message1")
        self.assertEqual("message1", page.get_last_message())
        self.assertEqual("red", page.get_last_message_color())

    def test_server_says_welcom(self):
        page = pages.ChatPage(self.browser, get = True)
        page.wait_for_chat_text("Welcome")
        self.assertEqual("Welcome to the chat!!", page.get_last_message())
        
class TwoBrowserTest(base.RunChatServerTestBase):

    @classmethod
    def setUpClass(cls):
        base.RunChatServerTestBase.setUpClass()
        cls.browser2 = base.start_browser()
    
    @classmethod
    def tearDownClass(cls):
        base.kill_browser(cls.browser2)
        base.RunChatServerTestBase.tearDownClass()

    def test_chat_between_browsers(self):
        b1_page = pages.ChatPage(self.browser, get = True)
        b1_page.wait_for_chat_text("Welcome")
        
        b2_page = pages.ChatPage(self.browser2, get = True)
        b2_page.wait_for_chat_text("Welcome")

        b1_page.send_chat_message("from-b1")
        b1_page.wait_for_chat_text("from-b1")
        self.assertEqual("from-b1", b1_page.get_last_message())
        self.assertEqual("red", b1_page.get_last_message_color())

        b2_page.wait_for_chat_text("from-b1")
        self.assertEqual("from-b1", b2_page.get_last_message())
        self.assertEqual("black", b2_page.get_last_message_color())
        
        b2_page.send_chat_message("from-b2")
        b2_page.wait_for_chat_text("from-b2")
        self.assertEqual("from-b2", b2_page.get_last_message())
        self.assertEqual("red", b2_page.get_last_message_color())

        b1_page.wait_for_chat_text("from-b2")
        self.assertEqual("from-b2", b1_page.get_last_message())
        self.assertEqual("black", b1_page.get_last_message_color())
        
if __name__ == '__main__':
    unittest.main()
