# this is the first code that is run by a session
from AccessControl.SecurityManagement import newSecurityManager
from zope.app.component.hooks import setSite 
from Testing.makerequest import makerequest
from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

app = transaction_manager.beginAndGetApp()

# something has changed causing self not to be present
try:
    portal = getToolByName(self, "portal_url").getPortalObject()
except NameError:
    portal = app.unrestrictedTraverse("/".join(portal_path))
    
# login the current user    
acl_users = portal.acl_users

uid = acl_users.getUserById(userid)
if uid:
    user = uid.__of__(acl_users)
    newSecurityManager(None, user)

response_output = StringIO()
app = makerequest(app, stdout=response_output)
try:
    setSite(portal)
except AttributeError:
    # Plone 2.5 sites do not have a site manager
    pass

# context is added in the new_namespace
if context:
    context = app.unrestrictedTraverse(context, None)
    if context is None:
        del context
else:
    # not needed
    del context

# clean out variables
del uid
del acl_users

try:
    del self
except NameError:
    pass
try:
   del portal_path
except NameError:
    pass

del transaction_manager
del userid
del StringIO
del makerequest
del newSecurityManager
del setSite
del getToolByName