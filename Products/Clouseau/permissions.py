
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('Products.Clouseau.permisssions')

security.declarePublic('Debug')
Debug = "Clouseau: Debug"
setDefaultRoles(Debug, ('Manager',))
