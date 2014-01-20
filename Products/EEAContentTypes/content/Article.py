""" Article """
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes.Schema import getNames
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone import PloneMessageFactory as _
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.ExternalHighlight import ExternalHighlight
from Products.EEAContentTypes.content.ExternalHighlight import schema as \
     ExtHighlightSchema
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.content.interfaces import IArticle
from eea.themecentre.interfaces import IThemeTagging
from zope.interface import implements
from Products.LinguaPlone.public import (
    Schema, LinesField, InAndOutWidget, registerType)

schema = Schema((
    LinesField(
        'publication_groups',
        schemata='categorization',
        vocabulary=NamedVocabulary("publications_groups"),
        languageIndependent=True,
        index="KeywordIndex:brains",
        widget=InAndOutWidget(
            label=_(u'Publication groups'),
            description=_(u'Fill in publication groups'),
            i18n_domain='eea',
            ),
        ),
),
)

Article_schema = getattr(Highlight, 'schema', Schema(())).copy() + \
                  schema.copy()

fields2Move2DefaultSchemata = ['eeaManagementPlan', 'image', 'imageLink',
                               'imageCaption', 'imageNote']
for fieldname in getNames(ExtHighlightSchema):
    field = Article_schema[fieldname]
    if fieldname in fields2Move2DefaultSchemata:
        field.schemata = 'default'
    elif field.schemata != 'metadata':
        field.schemata = 'Front Page'

Article_schema['text'].required = True
Article_schema.moveField('image', before='imageCaption')

#visibility level is "deprecated/hidden" by default
# used on feature article
Article_schema["visibilityLevel"].widget.visible = True

class Article(Highlight):
    """
    Articles are very similar to Highlights: folderish news-alike
    pages which contains information about specific subjects and can be
    displayed on frontpage of a website and sent as notification as any other
    news-alike content type.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ExternalHighlight, '__implements__', ()),) + (
        getattr(ATNewsItem, '__implements__', ()),)
    implements(IArticle)

    # This name appears in the 'add' box
    archetype_name = 'Article'

    meta_type = 'Article'
    portal_type = 'Article'
    allowed_content_types = [] + list(getattr(
        ExternalHighlight, 'allowed_content_types', [])) + list(
            getattr(ATNewsItem, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'highlight_view'
    suppl_views = ()
    typeDescription = "Article"
    typeDescMsgId = 'description_edit_highlight'

    _at_rename_after_creation = True

    schema = Article_schema
    content_icon = 'highlight_icon.gif'

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value

registerType(Article, PROJECTNAME)
