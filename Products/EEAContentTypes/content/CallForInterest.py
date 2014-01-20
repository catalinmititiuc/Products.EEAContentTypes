""" CallForInterest """
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import (Schema, StringField, StringWidget,
       DateTimeField, CalendarWidget, registerType)
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.document import ATDocument
from Products.EEAContentTypes.config import PROJECTNAME
from Products.CMFCore.permissions import View

schema = Schema((

    StringField(
        name='callForId',
        widget=StringWidget(
            label='Call for id',
            label_msgid='EEAContentTypes_label_callForId',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    DateTimeField(
        name='closeDate',
        widget=CalendarWidget(
            label='Close date',
            label_msgid='EEAContentTypes_label_closeDate',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    DateTimeField(
        name='openDate',
        widget=CalendarWidget(
            label='Open date',
            label_msgid='EEAContentTypes_label_openDate',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

    DateTimeField(
        name='applicationDate',
        widget=CalendarWidget(
            label='Application date',
            label_msgid='EEAContentTypes_label_applicationDate',
            i18n_domain='EEAContentTypes',
        ),
        required=1
    ),

),
)

CallForInterest_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    getattr(ATDocument, 'schema', Schema(())).copy() + schema.copy()


class CallForInterest(ATFolder, ATDocument):
    """ Call for interest
    """
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'CallForInterest'

    meta_type = 'CallForInterest'
    portal_type = 'CallForInterest'
    allowed_content_types = ['File', 'Document'] + \
            list(getattr(ATFolder, 'allowed_content_types', [])) + \
            list(getattr(ATDocument, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    #content_icon = 'CallForInterest.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "CallForInterest"
    typeDescMsgId = 'description_edit_callforinterest'

    _at_rename_after_creation = True

    schema = CallForInterest_schema

    security.declareProtected(View, 'getText')
    def getText(self):
        """ Text
        """
        return self.getField('text').get(self)

    security.declareProtected(View, 'CookedBody')
    def CookedBody(self, stx_level='ignored'):
        """ Body
        """
        return self.getText()

    def setOpenDate(self, value):
        """ Open date setter
        """
        self.setEffectiveDate(value)

    def setCloseDate(self, value):
        """ Closed date setter
        """
        self.setExpirationDate(value)

    def setEffectiveDate(self, value):
        """ Effective date setter
        """
        self.getField('effectiveDate').set(self, value)
        return self.getField('openDate').set(self, value)

    def setExpirationDate(self, value):
        """ Expiration date setter
        """
        self.getField('expirationDate').set(self, value)
        return self.getField('closeDate').set(self, value)

registerType(CallForInterest, PROJECTNAME)
