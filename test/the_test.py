import base

class OpenBrowserTest(base.RunChatServerTestBase):

    def test(self):
        self.browser.get("localhost:8080/chat.html")
        
if __name__ == '__main__':
    unittest.main()
