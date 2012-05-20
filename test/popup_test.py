import base
import pages

class PopupTest(base.RunChatServerTestBase):

    def test_open_close_popup(self):
        page = pages.WelcomePage(self.browser, get = True)
        page = page.open_popup()
        page.close()
        
if __name__ == '__main__':
    unittest.main()
