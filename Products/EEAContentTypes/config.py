""" Config
"""

from Products.CMFCore.permissions import setDefaultRoles
from Globals import DevelopmentMode

from zope.i18nmessageid.message import MessageFactory
EEAMessageFactory = MessageFactory('eea')

DEBUG = DevelopmentMode
PROJECTNAME = "EEAContentTypes"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

ADD_CONTENT_PERMISSIONS = {
    'CallForTender': 'Add CallForTender',
    'CFTRequestor': 'Add CFTRequestor',
    'QuickEvent': 'EEA: Add QuickEvent',
}

setDefaultRoles('Add CallForTender', ('Manager','Editor'))
setDefaultRoles('Add CFTRequestor', ('Manager'))

product_globals = globals()

ADD_CONTENT_PERMISSIONS['QuickEvent'] = 'EEA: Add QuickEvent'
setDefaultRoles('EEA: Add QuickEvent', ('Manager'))

DEFAULT_PAGE_TYPES = ( 'FlashFile', 'Highlight' )
JAVASCRIPTS = [ {'id' : 'swfobject.js'},
                {'id' : 'resize.js' },
                {'id' : 'hideemail.js' } ]

DEPENDENCIES = [ 'ATVocabularyManager', ]

# URL normalizer
MAX_URL_WORDS = 5
URL_ORPHANS = 1
