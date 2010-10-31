
import threading
import os
import Queue
import code
from pprint import pformat
from logging import getLogger
import introspect
import sys, StringIO

from ZODB.POSException import ConflictError
from Products.Clouseau import ClouseauMessageFactory as _

log = getLogger("Products.Clouseau.sessions")

# if this is 1, then we skip the first line in the 
# interactions... if its 0 then we don't. This will
# hopefully get fixed later...
show_first = 1

# replace stdoout, from unit tests you probably want
# this to be false, makes getting a pdb much easier
# probably though this a matter of fixing a mess
replace_stdout = True

no_session_string = _(u"""A session was requested by a browser, but no session exists. This normally occurs when you leave a browser with a Clouseau session open and restart Zope or delete the session. Please close that browser window.""")

sessions_lock = threading.Lock()
sessions = {}
next_session_id = -1
            
class IOPairInterpreter(code.InteractiveInterpreter):

    can_commit = True

    def __init__(self, namespace):
        self.interactions = []
        self.currentOutput = []
        self.currentInput = []
        self.codeMap = {}
        code.InteractiveInterpreter.__init__(self, locals=namespace)
        self.locals['write'] = self.pformat_write

    def resetLines(self):
        self.interactions = []

    def getTip(self, text):
        # lets use the inspect API
        # we've got text eval it
        if text.find('=') > -1:
            text = text.split('=')[-1].strip()
        try:
            evald = eval(text, self.locals)
        except ConflictError:
            raise
        except:
            # i really feel i should do something like
            # pass back a meaningful error
            return None

        # go get a tooltip
        data = introspect.lookup(evald, text)
        return data
        
    def prepareCode(self, text, filename='<input>'):
        self.currentInput.append(text)
        source = "\n".join(self.currentInput)
        #true_source = source
        code = None
        true_lines = []
        triple_flag = False
        for line in source.split('\n'):
            # strip line
            sline = line.strip()
            # there an easier way to figure this out?
            indent = 0
            # a cowardly attempt to ignore printing out code that
            # is in a triple quoted string in a block, so we don't
            # get """asd\nwrite(asdads)\nasdasd"""
            if sline.find('"""') > -1 \
                or sline.find("'''") > -1 \
                or (len(sline) > 0 and sline[-1] == '\\'):
                # although not a triple string, this allows
                # a \ on the end of lines to allow them to
                # work ok
                triple_flag = True
            if not triple_flag:
                for char in line:
                    if char not in (' ', '\t'):
                        break
                    indent += 1
                try:
                    code = self.compile(sline, filename, 'eval')
                except (SyntaxError, ):
                    # there was a syntax error
                    pass
                else:
                    if code is not None:
                        # we got some code that works as eval
                        # let's rewrite it to print instead
                        # write has to go inside the indent
                        line = "%swrite( %s )" % (line[:indent], line[indent:])
                        # source needs to be exec'd
            true_lines.append(line)
        true_source = '\n'.join(true_lines)
        try:
            code = self.compile(true_source, filename, 'exec')
        except (OverflowError, SyntaxError, ValueError), e:
            self.showsyntaxerror(filename)
            self.currentInput = []
            self.interactions.append( {
                "input": text,
                "output": self.getAndResetOutput(),
                "status": "input-error"
            })
            # by returning None we are stopping execution of this
            # fragment
            return None
        
        # we've got a proper code fragment put it in
        if code is not None:
            # code is complete
            self.currentInput = []
            self.codeMap[code] = source

            self.interactions.append( {
                "input": text,
                "status": "input", }
            )
            # by returning code are expecting it to be executed
            return code
        else:
            # code is correct so far, but incomplete
            # add it on to the input and set the flag for that line as not complete
            self.interactions.append( {
                "input": text, 
                "status": "input-not-complete", }
            )
            # by returning None we are stopping execution of this
            # fragment
            return None

    def runCodeAndStoreInteraction(self, code):
        source = self.codeMap[code]
        self.runcode(code)
        output = self.getAndResetOutput()
        # do we need to append lines that are empty?
        # do we really need to test for None
        if output and output.strip() != "None":
            self.interactions.append( {
                "output": output,
                "status": "output"
            } )

    def runcode(self, code):
        """Queue a code object for execution"""
        
        #replace the stdout to capture "console" output
        
        if replace_stdout:
            old_std_out = sys.stdout 
            new_std_out = StringIO.StringIO()
            sys.stdout = new_std_out
            to_stdout = ""
        
        try:
            result = eval(code, self.locals)
            if result is not None:
                self.write(pformat(result))
                if replace_stdout:
                    val = new_std_out.getvalue()    #the captured print output
                    to_stdout += val
                    self.write(val)
            else:
                if replace_stdout:
                    val = new_std_out.getvalue()    #the captured print output
                    if val.strip() <> "":
                        to_stdout += val
                        self.write(val)
        except SystemExit:
            #replace the stdout back to the old one
            if replace_stdout:
                sys.stdout = old_std_out
                new_std_out.close(); del(new_std_out)
                raise
        except:
            self.can_commit = False
            self.showtraceback()
        else:
            if (self.currentOutput and
                self.currentOutput[-1][-1] != "\n"):
                # make sure we break a line after each eval
                self.write("\n")

        if replace_stdout:
            sys.stdout = old_std_out  #replace the stdout back to the old one
            new_std_out.close(); del(new_std_out)
            try:
                print (to_stdout)  #put the real output to the console
            except ValueError:
                # its been closed, reopen it
                sys.stdout = StringIO.StringIO()

    def write(self, data):
        if not data.endswith("\n"):
            data += "\n"
        self.currentOutput.append(data)

    def pformat_write(self, data):
        self.write(pformat(data))

    def getAndResetOutput(self):
        out = "".join(self.currentOutput)
        self.currentOutput = []
        return out

class Session(threading.Thread):

    def __init__(self, namespace, transactionManager=None):
        threading.Thread.__init__(self)

        self.tm = transactionManager
        if self.tm is None: # testing hook
            self.tm = TransactionManager()
        self.namespace = namespace
        self.namespace["transaction_manager"] = self.tm
        self.queue = Queue.Queue(1)
        self.interpreter = IOPairInterpreter(self.namespace)
        self.start()

    # hack, move everything up by one to avoid showing the 
    # first line of the input, probably a nicer way to do this
    def getLinesLength(self):
        return len(self.interpreter.interactions) - show_first

    def getLines(self, line_numbers):
        return [self.interpreter.interactions[i + show_first] for i in line_numbers]

    def getAllLines(self):
        return self.interpreter.interactions[show_first:]
        
    def getTip(self, text):
        return self.interpreter.getTip(text)

    def run(self, source=None):
        if source is None:
            source = self.getBootstrapSource()
        code = self.interpreter.prepareCode(source)
        assert code is not None, "Prepared code is incomplete"
        while code is not None:
            self.interpreter.runCodeAndStoreInteraction(code)
            code = self.getCode()

        self.tm.abortAndClose()
     
    def getBootstrapSource(self):
        return file(os.path.join(os.path.dirname(__file__), "bootstrap.py")).read()

    def putSource(self, text):
        code = self.interpreter.prepareCode(text)
        if code is not None:
            self.queue.put(code)
            log.info("queue: put source: " + text)
            return False
        return True

    def getCode(self):
        return self.queue.get()

    def stopSession(self):
        self.queue.put(None)
        self.join()

def new_session(namespace):
    global next_session_id

    sessions_lock.acquire()
    try:
        next_session_id += 1
        sessions[next_session_id] = Session(namespace)
    finally:
        sessions_lock.release()
    return next_session_id

def get_session(session_id):
    try:
        return sessions[session_id]
    except KeyError:
        raise KeyError, no_session_string

def list_session_ids():
    return sessions.keys()

def del_session(session_id):
    del sessions[session_id]

class TransactionManager:

    def begin(self):
        import transaction
        self.txn = transaction.begin()

    def commit(self):
        self.txn.commit()
        del self.txn

    def abort(self):
        self.txn.abort()
        del self.txn

    def recordSpecificMetadata(self, path, username, userPath):
        self.txn.note(path)
        self.txn.setUser(username, userPath)

    def getNewApp(self):
        import Zope2
        return Zope2.app()

    def beginAndGetApp(self):
        self.begin()
        self.app = self.getNewApp()
        return self.app

    def close(self):
        self.app._p_jar.close()
        del self.app

    def abortAndClose(self):
        self.abort()
        self.close()

    def commitAndClose(self):
        self.commit()
        self.close()
