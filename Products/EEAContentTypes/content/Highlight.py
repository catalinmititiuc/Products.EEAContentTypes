""" Highlight """
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.Archetypes.Schema import getNames
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.ExternalHighlight import ExternalHighlight
from Products.EEAContentTypes.content.ExternalHighlight import schema as \
     ExtHighlightSchema
from Products.EEAContentTypes.content.interfaces import IExternalHighlight
from Products.EEAContentTypes.content.quotation import quotation_schema
from Products.EEAContentTypes.content.validators import ExistsKeyFactsValidator
from Products.LinguaPlone.public import Schema, registerType
from eea.themecentre.interfaces import IThemeTagging
from zope.interface import implements

schema = Schema((),)


Highlight_schema =  getattr(ATNewsItem, 'schema', Schema(())).copy() + \
    getattr(ExternalHighlight, 'schema', Schema(())).copy() + \
    quotation_schema.copy() + \
    schema.copy()

# put all the external highlights fields into their own schema
ExternalHighlightSchema = ExtHighlightSchema.copy()

fields2Move2DefaultSchemata = ['management_plan']
for fieldname in getNames(ExternalHighlightSchema):
    field = Highlight_schema[fieldname]
    if fieldname in fields2Move2DefaultSchemata:
        field.schemata = 'default'
    elif field.schemata != 'metadata':
        field.schemata = 'Front Page'


Highlight_schema['text'].required = True
validators = Highlight_schema['text'].validators
validators.appendRequired(ExistsKeyFactsValidator('existsKeyFacts'))
Highlight_schema.moveField('image', before='imageCaption')


class Highlight(ExternalHighlight, ATNewsItem):
    """<p>Hightlights are links with descriptions presented as news on
    the website.</p>
    """
    implements(IExternalHighlight)
    archetype_name = 'Highlight'
    schema = Highlight_schema

    schema["publishDate"].widget.visible = False
    schema["expiryDate"].widget.visible = False

    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    security.declarePublic('getPublishDate')
    def getPublishDate(self):
        """ Publish date
        """
        return self.getEffectiveDate()

    security.declarePublic('setPublishDate')
    def setPublishDate(self, value, **kw):
        """ Set publish date
        """
        self.setEffectiveDate(value)

    getExpiryDate = ExternalHighlight.getExpiryDate
    setExpiryDate = ExternalHighlight.setExpiryDate

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """ Download the file
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        img_field = self.getField('image')
        return img_field.download(self, REQUEST, RESPONSE)


registerType(Highlight, PROJECTNAME)
