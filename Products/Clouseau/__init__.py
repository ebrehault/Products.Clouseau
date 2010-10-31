from Products.Clouseau.config import *
from Products.CMFCore.DirectoryView import registerDirectory

from zope.i18nmessageid import MessageFactory
ClouseauMessageFactory = MessageFactory('clouseau')
PloneMessageFactory = MessageFactory('plone')

registerDirectory('skins/Clouseau', product_globals)

from Products.CMFCore import utils
from Products.Clouseau.tools.clouseautool import ClouseauTool
import permissions

tools = ( ClouseauTool, )

def initialize(context):
    utils.ToolInit(
		product_name,
		tools=tools,
        icon='clouseau.jpg').initialize(context)
