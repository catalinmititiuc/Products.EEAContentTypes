""" Promotion """

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.ExternalHighlight import ImageBlobField
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from Products.EEAContentTypes.content.interfaces import IExternalPromotion
from Products.LinguaPlone.public import AnnotationStorage
from Products.LinguaPlone.public import ImageWidget
from Products.LinguaPlone.public import Schema
from Products.LinguaPlone.public import StringField
from Products.LinguaPlone.public import StringWidget, registerType
from Products.validation import V_REQUIRED
from eea.promotion.interfaces import IFrontpageSectionIndex
from zope.component import adapts
from zope.interface import implements

schema = Schema((
    ImageBlobField('image',
        required = False,
        storage = AnnotationStorage(migrate=True),
        languageIndependent = True,
        swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
        pil_quality = zconf.pil_config.quality,
        pil_resize_algo = zconf.pil_config.resize_algo,
        max_size = (1280,1024),
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (180,135),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
               },
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkFileMaxSize', V_REQUIRED)),
        widget = ImageWidget(
            description = (
                "Will be shown in the news listing, and in the news "
                "item itself. Image will be scaled to a sensible size."),
            description_msgid = "help_news_image",
            label= "Image",
            label_msgid = "label_news_image",
            i18n_domain = "plone",
            show_content_type = False)
        ),
    StringField(
        name='url',
        widget=StringWidget(
            label='Url',
            label_msgid='EEAContentTypes_label_url',
            i18n_domain='EEAContentTypes',
        )
    ),

),
)

Promotion_schema = getattr(ATNewsItem, 'schema', Schema(())).copy() + \
                   schema.copy()

Promotion_schema['allowDiscussion'].schemata = 'metadata'
Promotion_schema['relatedItems'].schemata = 'metadata'
Promotion_schema['text'].schemata = 'metadata'

class Promotion(ATNewsItem, ThemeTaggable):
    """ Promotion
    """
    security = ClassSecurityInfo()
    implements(IExternalPromotion)

    # This name appears in the 'add' box
    archetype_name = 'Promotion'

    meta_type = 'Promotion'
    portal_type = 'Promotion'
    #allowed_content_types = [] + list(getattr(ATNewsItem,
            #'allowed_content_types', [])) + list(getattr(ThemeTaggable,
            #'allowed_content_types', []))
    #filter_content_types = 0
    #global_allow = 0
    #content_icon   = 'document_icon.gif'
    #immediate_view = 'base_view'
    #default_view = 'base_view'
    #suppl_views = ()
    #typeDescription = "Promotion"
    #typeDescMsgId = 'description_edit_promotion'

    _at_rename_after_creation = True

    schema = Promotion_schema

    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """Manually specifing mutator, solves ticket #3972"""
        ThemeTaggable.setThemes(self, value, **kw)

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """ Download the file
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getField('image')
        return field.download(self, REQUEST, RESPONSE)


registerType(Promotion, PROJECTNAME)


class FrontpageSectionIndex(object):
    """ Front page section index """
    implements(IFrontpageSectionIndex)
    adapts(IExternalPromotion)

    def __init__(self, context, request):
        """ """
        self.context = context

    def __call__(self):
        """ """
        return u'/'.join(self.context.getPhysicalPath()[:-1])
