import time
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Globals import package_home
import Globals
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

Globals.DevelopmentMode = True
ZopeTestCase.installProduct('Clouseau')

from Products.Clouseau import sessions
sessions.replace_stdout = False

process_text = [
    [ "import urllib", ],
    [ "f = 1", ],
    [ "x = 1", "x += 1" ],
    [ "y = 0", "z = 10", "for x in range(0, z):", "    y = x", ],
    ]

# the code will check that the
# last thing output from the commands run
# is "True", anything else raises an error
process_text_asserts = [
    "urllib.urlopen == urllib.urlopen",
    "f == 1",
    "x == 2",
    "x == 9",
]


tooltip_text = [
    [ "'asd'.lower(", ],
    ]

autocomplete_text = [
    [ "'asd'.", ],
    ]

class TestAjax(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        # get a pointer to the tool
        self.folder.manage_addProduct['Clouseau'].manage_addTool('Clouseau', None)
        self.tool = self.folder.clouseau_tool
        self.filenames = []

    def test_list_session_info(self):
        """ Expecting a simple list of sessions, each of which is
        a dictionary of:
            id: session id
            lines: number of lines in the session
            ...
        """
        sessions = self.tool.list_session_info()
        for session in sessions:
            assert isinstance(session, dict)
            assert session.get("session_id")
            assert session.get("lines_length")

    def tearDown(self):
        """ Tear down the session """
        sessions = self.tool.list_session_info()
        for session in sessions:
            self.tool.stop_session(session.get("session_id"))
        
        for filename in self.filenames:
            self.tool.delete_saved_session(filename)

    def test_new_session(self):
        """ Create a new session """
        # expecting new_session to return me the session
        sid = self.tool.new_session()
        # expecting the session to have an id
        # and it to be in the sessions
        sessions = self.tool.list_session_info()
        assert sid in [ s["session_id"] for s in sessions ]

    def test_get_savable_session(self):
        """ Get the data for a session in a savable manner """
        for lines in process_text:
            sid = self.tool.new_session()
            data = []
            for line in lines:
                data.append(line)
                self.tool.process_text(sid, line)
                res = self.tool.get_all_lines_text(sid, full=False)
                # the result should match all the lines given
                # with a bit of line end munging that is...
                d = "\n".join(data)
                r = res.strip()
                assert d == r, "Failed [%s] != [%s]" % (d, r)

    def test_save_session(self):
        """ Save a session so that it can be loaded back in later """
        for lines in process_text:
            sid = self.tool.new_session()
            for line in lines:
                self.tool.process_text(sid, line)
            self.filenames.append(self.tool.save_session(sid))

    def test_load_session(self):
        """ Load a session so that it can be run """
        self.test_save_session()
        for filename, result in map(None, self.filenames, process_text_asserts):
            sid = self.tool.new_session()
            self.tool.load_session(sid, filename)
            self._assert_last(sid, result)
    
    def _assert_last(self, sid, result):       
        self.tool.process_text(sid, result) 
        time.sleep(1)
        session = self.tool.get_session(sid)
        res = session.getAllLines()[-1]
        assert res.has_key("output"), "No output: " + str(res)
        assert res["output"].strip() == "True", "Not True: " + result
            
    def test_process_texts(self):
        """ Process all the texts of a session """
        for lines, result in map(None, process_text, process_text_asserts):
            sid = self.tool.new_session()
            for line in lines:
                self.tool.process_text(sid, line)
            self._assert_last(sid, result)
                
    def test_list_saved_sessions(self):
        """ List all the sessions """
        # not sure what to test there
        self.tool.list_saved_sessions()

    def _new_session(self):
        """ Utility function to give me new sessions """
        sid = self.tool.new_session()
        return sid

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAjax))
    return suite

if __name__ == '__main__':
    framework()
