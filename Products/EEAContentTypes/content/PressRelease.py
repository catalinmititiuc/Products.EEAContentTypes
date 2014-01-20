""" PressRelease """
from AccessControl import ClassSecurityInfo
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.quotation import quotation_schema
from Products.LinguaPlone.public import (
    Schema, BaseSchema, BaseContent, registerType)

from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging


PressRelease_schema = BaseSchema.copy() + \
    getattr(Highlight, 'schema', Schema(())).copy() + \
    quotation_schema.copy()


class PressRelease(Highlight, BaseContent):
    """ Press release
    """
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'Press Release'

    meta_type = 'PressRelease'
    portal_type = 'PressRelease'
    allowed_content_types = [] + list(getattr(Highlight,
                                              'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'pressrelease_view'
    suppl_views = ()
    typeDescription = "Press Release"
    typeDescMsgId = 'description_edit_pressrelease'
    _at_rename_after_creation = True
    schema = PressRelease_schema
    content_icon = 'press-release_icon.gif'

    # Methods

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value


registerType(PressRelease, PROJECTNAME)
