# $Id$

from urllib import urlopen
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from Globals import DevelopmentMode

# package imports
from Products.Clouseau import permissions, sessions
from urlparse import urlparse

from Products.CMFCore.utils import UniqueObject, getToolByName

from Products.Clouseau.output import wrapper as xmlwrapper
from Products.Clouseau.config import product_name, unique_id
from Products.Clouseau.config import save_directory, load_directories
from Products.Clouseau.config import enabled, enabled_only_in_debug_mode

from admin import admin

import os
import time

run = False

if enabled:
    run = True

if enabled and not DevelopmentMode and enabled_only_in_debug_mode:
    run = False

if run:
    class ClouseauTool(UniqueObject,  SimpleItem):
        """ .enaThe tool for handling the data """
        meta_type = product_name
        id = unique_id
        title = "The Amazing Python Inspector"
    
        security = ClassSecurityInfo()
    
        enabled = True
    
        def __init__(self):
            pass
    
        security.declarePrivate('new_namespace')
        def new_namespace(self, context=None):
            user = getSecurityManager().getUser()
            return dict(portal_path=self.aq_parent.getPhysicalPath(),
                        __name__="__zope_debug__",
                        __doc__=None,
                        self=self,
                        context=context,
                        utils=admin(self),
                        userid=user.getId(),
                        acl_users_path=user.aq_parent.getPhysicalPath(),
                        )
    
        security.declareProtected(permissions.Debug, "new_session")
        def new_session(self, context=None):
            """ creates a new session and returns the session id """
            namespace = self.new_namespace(context)
            id = sessions.new_session(namespace)
            return id
    
        security.declareProtected(permissions.Debug, "new_session_xml")
        def new_session_xml(self, context):
            """ Creates a new session and returns it as xml """
            # not sure how it could get here as null but just in case...
            if context == "null":
                context = None
            if context:
                context = urlparse(context)[2]
                
            id = self.new_session(context)
            return self.get_session_xml(id)
    
        security.declareProtected(permissions.Debug, "process_text")
        def process_text(self, session_id, text):
            """ push a source_text to a session object """
            session = self.get_session(session_id)
            session.putSource(text)
    
        security.declareProtected(permissions.Debug, "process_text_xml")
        def process_text_xml(self, session_id, text):
            """ push a source_text to a session object """
            session = self.get_session(session_id)
            session.putSource(text)
            return self.get_session_xml(session_id)
            
        security.declareProtected(permissions.Debug, "get_lines")
        def get_lines(self, session_id, line_numbers):
            """ get output lines from a session """
            session = self.get_session(session_id)
            return session.getLines(line_numbers)
    
        security.declareProtected(permissions.Debug, "get_all_lines")
        def get_all_lines(self, session_id):
            """ get output lines from a session """
            session = self.get_session(session_id)
            return session.getAllLines()
    
        security.declareProtected(permissions.Debug, "get_all_lines_xml")
        def get_all_lines_xml(self, session_id):
            """ get output lines from a session as xml, useful for debugging """
            lines = self.get_all_lines(session_id)
            return self.get_lines_xml(session_id)
            
        security.declareProtected(permissions.Debug, "get_all_lines_text")
        def get_all_lines_text(self, session_id, full=True):
            """ get output from a session as output from an interactive python session"""
            # if full
            #   get the >>> and the output
            # else
            #   just get the input, this is useful for 
            #   saving a session
            lines = self.get_all_lines(session_id)
            msg = ""
            for line in lines:
                if line['status']=='input-not-complete':
                    #check if the line is indented
                    if len(line['input']) > 0 and line['input'][0] == ' ':
                        if full:
                            msg += "..." + line['input'] + "\n"
                        else:
                            msg += line['input'] + '\n'
                    else:
                        if full:
                            msg += ">>> " + line['input'] + "\n"
                        else:
                            msg += line['input'].rstrip() + '\n'
                if line['status']=='input':
                    if not full:
                        msg += line['input'].rstrip() + '\n'
                    else:
                        if line['input'] == "":
                            msg += "...\n"
                        else:
                            msg += ">>> " + line['input'] + "\n"
                if line['status']=='output' and full:
                    msg += line['output']
            return msg
    
        security.declareProtected(permissions.Debug, "get_session_xml")
        def get_lines_xml(self, session_id, line_numbers=None):
            """ Returns data on a session """
            if line_numbers is not None:
                line_numbers = [ int(l) for l in line_numbers ]
                lines = self.get_lines(session_id, line_numbers)
            elif line_numbers is None:
                # get all the lines
                lines = self.get_all_lines(session_id)
                line_numbers = range(0, len(lines))
            else:
                raise ValueError, "Must specify either line_numbers or lines"
                
            # return line as xml
            xml = xmlwrapper()
        
            elem = xml.xml.createElement("lines")
            k = 0
            for item in lines:
                ln = line_numbers[k]
                k += 1
                # if command or response are empty, just ignore them
                # should never happen that they are both empty
                line = xml.xml.createElement("line")
                line.setAttribute("number", str(ln))
                status = item["status"]
                line.setAttribute("status", str(status))
                command = item.get("input", None)
                response = item.get("output", None)
    
                
                if command is None and response is None:
                    raise ValueError, "Both the command, and the response is None, this should not happen"
                
                if command is not None:
                    command_node = xml.xml.createElement("command")
                    command_text = xml.xml.createTextNode(command)
                    command_node.appendChild(command_text)
    
                    line.appendChild(command_node)
    
                # only give a response 
                if response is not None:
                    response_node = xml.xml.createElement("response")
                    response_text = xml.xml.createTextNode(response)
                    response_node.appendChild(response_text)
            
                    line.appendChild(response_node)
    
                elem.appendChild(line)
    
            xml.add(self._get_session_xml(xml, session_id))
            xml.add(elem)
    
            self._set_content_type()
            return str(xml)
    
        security.declareProtected(permissions.Debug, "get_session_xml")
        def get_session_xml(self, session_id):
            """ Returns data on a session """
            session = self.get_session(session_id)
            # return id as xml
            xml = xmlwrapper()
            xml.add(self._get_session_xml(xml, session_id))
        
            self._set_content_type()
            return str(xml)
    
        # protected utility functions
        def _get_session_xml(self, xml, session_id):
            session = self.get_session(session_id)
            elem = xml.xml.createElement("session")
            elem.setAttribute("id", str(session_id))
            elem.setAttribute("lines", str(session.getLinesLength()))
            return elem
    
        def _set_content_type(self):
            self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/xml')
    
        security.declareProtected(permissions.Debug, "get_session")
        def get_session(self, session_id):
            """ returns a session given it's session_id """
            session = sessions.get_session(int(session_id))
            return session
    
        def _createTextNode(self, xml, name, data, id):
            elem = xml.xml.createElement(name)
            elem.setAttribute("id", id)
            elem_text = xml.xml.createTextNode(data)
            elem.appendChild(elem_text)
            return elem
    
        security.declareProtected(permissions.Debug, "get_tip_xml")
        def get_tip_xml(self, session_id, text):
            """ returns a tooltip given it's session_id """
            session = self.get_session(session_id)
            data = session.getTip(text)
            
            xml = xmlwrapper()
            elem = xml.xml.createElement("tips")
            
            if data is None:
                return
    
            for key, value in data:
                elem.appendChild(self._createTextNode(xml, "tip", str(value), str(key)))
            
            xml.add(elem)
            self._set_content_type()
            return str(xml)
    
        security.declareProtected(permissions.Debug, "list_session_info")
        def list_session_info(self):
            """ returns a session given it's session_id """
            return [dict(session_id=sid,
                         lines_length=self.get_session(sid).getLinesLength())
                    for sid in sessions.list_session_ids()]
    
        security.declareProtected(permissions.Debug, "get_session_namespace")
        def get_session_namespace(self, session_id):
            return [dict(name=name, value=value) for name, value in
                    self.get_session(session_id).interpreter.locals.items()]
    
        security.declareProtected(permissions.Debug, "stop_session")
        def stop_session(self, session_id, REQUEST=None, RESPONSE=None):
            """ kill a session? """
            session = self.get_session(session_id)
            # what is this meant to be doing?
            session.stopSession()
            sessions.del_session(int(session_id))
            if RESPONSE:
                url = "clouseau_list?portal_status_message=Session deleted"
                RESPONSE.redirect(url)
                
        security.declareProtected(permissions.Debug, "can_save_session")
        def can_save_session(self):
            """ Can we save a session? """
            random = "save-test.%s.py" % time.time()
            file = os.path.join(save_directory, random)
            try:
                open(file, "wb").write("test")
            except IOError:
                return False
            # if this fails does that mean something?
            os.remove(file)            
            return True
        
        security.declareProtected(permissions.Debug, "save_session")
        def save_session(self, session_id, filename=None, REQUEST=None, RESPONSE=None):
            """ Save a session? """
            session = self.get_session(session_id)
            if not filename:
                random = "saved-session-%s.%s.py" % (time.time(), session_id)
                
            original_filename = os.path.join(save_directory, random)
            final_filename = original_filename
            if not filename:
                # we only calculate a random filename if we
                # need to
                for x in range(0, 20):
                    if os.path.exists(final_filename):
                        final_filename = orig_file[:-3] + ".%s" % x + ".py"
                    else:
                        break
                else:
                    raise ValueError, "Could not find a unique value for the filename."
                
            data = self.get_all_lines_text(session_id, full=False)
            
            # let save errors bubble up
            open(final_filename, "wb").write(data)
            
            if RESPONSE:
                url = "clouseau_list?portal_status_message=Session saved"
                RESPONSE.redirect(url)
            else:
                return final_filename
    
        security.declareProtected(permissions.Debug, "load_session")
        def load_session(self, session_id, filename, REQUEST=None, RESPONSE=None):
            """ Load a session? """
            source = None
            for directory in load_directories:
                full_filename = os.path.join(directory, filename)
                if os.path.exists(full_filename):
                    source = urlopen(full_filename).readlines()
                    break
            else:
                source = urlopen(filename).readlines()
                
            if not source:
                raise ValueError, "Saved session not found: %s" % filename
                
            for line in source:
                self.process_text(session_id, line.rstrip())
    
        security.declareProtected(permissions.Debug, "list_save_directories")
        def list_save_directories(self, short=False, REQUEST=None, RESPONSE=None):
            """ List directories that have been saved """
            return load_directories
                
        security.declareProtected(permissions.Debug, "list_saved_sessions")
        def list_saved_sessions(self, short=False, REQUEST=None, RESPONSE=None):
            """ Find the filenames that have been saved """
            filenames = []
            for directory in load_directories:
                # in the buildout (well mine anyway), this is not readable
                # by the zope instance, since buildout is run as root
                # may need to come up with a plan B here, but this will
                # allow Clouseau to work
                try:
                    listing = os.listdir(directory)
                except OSError:
                    # should probably log this
                    listing = []
                for file in listing:
                    if file not in filenames and file.endswith('.py'):
                        full_file = os.path.join(directory, file)
                        if not short:
                            filenames.append(full_file)
                        else:
                            filenames.append(file)
            filenames.sort()
            return filenames
    
        security.declareProtected(permissions.Debug, "delete_saved_session")
        def delete_saved_session(self, filename, REQUEST=None, RESPONSE=None):
            """ Delete a saved session """
            if not os.path.exists(filename):
                filename = os.path.join(save_directory, filename)
                if not os.path.exists(filename):
                    raise ValueError, "Cannot find a file called %s" % filename
            
            os.remove(filename)
            
            if RESPONSE:
                url = "clouseau_list?portal_status_message=Saved session deleted"
                RESPONSE.redirect(url)
else:    
    class ClouseauTool(UniqueObject,  SimpleItem):
        """ The tool for handling the data """
        meta_type = product_name
        id = unique_id
        title = "The Amazing Python Inspector (Not enabled)"

        security = ClassSecurityInfo()
        
        enabled = False

InitializeClass(ClouseauTool)
