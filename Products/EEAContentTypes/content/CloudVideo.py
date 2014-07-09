""" FlashFile """
from plone.app.blob.field import ImageField
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.file import ATFile
from Products.CMFCore.permissions import View

from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import ICloudVideo
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from Products.Archetypes.atapi import (
    Schema, ImageWidget,
    registerType, TextField, TextAreaWidget, RichWidget
)
from Products.Archetypes.atapi import AnnotationStorage
from Products.LinguaPlone import public


schema = Schema((
        ImageField('image',
            required=False,
            storage=public.AnnotationStorage(migrate=True),
            languageIndependent=True,
            widget=ImageWidget(
                label='Image',
                label_msgid='EEAContentTypes_label_image',
                description_msgid='EEAContentTypes_help_image',
                i18n_domain='eea',
                show_content_type = False
            )
        ),
        TextField('cloudUrl',
                languageIndependent=True,
                required=True,
                schemata='default',
                storage=AnnotationStorage(migrate=True),
                default_content_type='text/plain',
                validators=('videoCloudUrlValidator',),
                allowable_content_types=('text/plain',),
                default_output_type='text/plain',
                widget=TextAreaWidget(
                    description='The embedding code for the video from' \
                                    ' external sites eg. Vimeo or Youtube',
                    description_msgid="EEAContentTypes_help_quotationtext",
                    label="Cloud Url",
                    label_msgid="EEAContentTypes_label_cloud_url"
                )
        ),
        TextField(
            name='text',
            widget=RichWidget
            (
                label="Rich Text Description",
                label_msgid="EEAContentTypes_label_rich_description",
                i18n_domain="eea",
                rows=10,
            ),
        ),
    )
)

CloudVideo_schema = (getattr(ATFile, 'schema', Schema(())).copy() +
                     schema.copy())

# normalize_default_schemata_order(CloudVideo_schema)
# hide file field from CloudVideo
CloudVideo_schema['file'].required = False
CloudVideo_schema['file'].widget.visible = {"edit": "invisible", "view":
                                                                "invisible"}


class CloudVideo(ATFile, ThemeTaggable):
    """ CloudVideo contenttype
    """
    security = ClassSecurityInfo()
    implements(ICloudVideo)

    # This name appears in the 'add' box
    archetype_name             = 'CloudVideo'
    meta_type                  = 'CloudVideo'
    portal_type                = 'CloudVideo'
    allowed_content_types      = [] + list(getattr(ATFile,
                                                'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    immediate_view             = 'file_view'
    default_view               = 'file_view'
    suppl_views                = ()
    typeDescription            = "CloudVideo"
    typeDescMsgId              = 'description_edit_cloudvideo'

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ Redirect to /view for CloudVideo to avoid file download 
        """
        return self.REQUEST.response.redirect(
                                        self.absolute_url() + "/view", 301)

    schema = CloudVideo_schema

registerType(CloudVideo, PROJECTNAME)
