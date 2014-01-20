""" FlashFile """
from plone.app.blob.field import BlobField
from zope.interface import implements
from OFS.Image import File as ZFile
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.file import ATFile
from Products.validation import V_REQUIRED
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IFlashAnimation
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from Products.Archetypes.utils import contentDispositionHeader
from Products.Archetypes.atapi import (
    Schema, IntegerField, IntegerWidget, FileWidget,
    StringField, StringWidget, registerType, AnnotationStorage
)


class FlashFileField(BlobField):
    """ Flash File Field"""
    #BBB Backward compatible index_html.
    #XXX this should be removed from Products.EEAContentTypes > 2.25
    def index_html(self, instance, REQUEST=None, RESPONSE=None,
                   disposition='inline', **kwargs):
        """ Field public view """
        storage = self.getStorage()
        zfile = storage.get('file', instance)
        if not isinstance(zfile, ZFile):
            return super(FlashFileField, self).index_html(instance,
                    REQUEST, RESPONSE, disposition, **kwargs)

        #BBB Backward compatible: OFS.Image.File
        if not REQUEST:
            REQUEST = instance.REQUEST
        if not RESPONSE:
            RESPONSE = REQUEST.RESPONSE
        filename = getattr(zfile, 'filename', instance.getId())
        header_value = contentDispositionHeader(
            disposition='attachment',
            filename=filename)
        RESPONSE.setHeader("Content-disposition", header_value)
        return zfile.index_html(REQUEST, RESPONSE)

schema = Schema((
    FlashFileField('file',
              required=True,
              primary=True,
              languageIndependent=True,
              storage = AnnotationStorage(migrate=True),
              validators = (('isNonEmptyFile', V_REQUIRED),
                            ('checkFileMaxSize', V_REQUIRED)),
              widget = FileWidget(
                        description = "",
                        label= "File",
                        label_msgid = "label_file",
                        i18n_domain = "plone",
                        show_content_type = False,
        )
    ),
    IntegerField('width',
        widget=IntegerWidget(
            label='Width',
            label_msgid='EEAContentTypes_label_width',
            description_msgid='EEAContentTypes_help_width',
            i18n_domain='EEAContentTypes',
        )
    ),

    IntegerField('height',
        widget=IntegerWidget(
            label='Height',
            label_msgid='EEAContentTypes_label_height',
            description_msgid='EEAContentTypes_help_height',
            i18n_domain='EEAContentTypes',
        )
    ),

    StringField('bgcolor',
        default="",
        widget=StringWidget(
            label="Background color",
            description=("The HEX code(#112233) for background color of the "
                         "flash application. Default is transparent"),
            label_msgid='EEAContentTypes_label_bgcolor',
            description_msgid='EEAContentTypes_help_bgcolor',
            i18n_domain='EEAContentTypes',
        )
    ),

),
)

FlashFile_schema = (getattr(ATFile, 'schema', Schema(())).copy() +
                    schema.copy())

class FlashFile(ATFile, ThemeTaggable):
    """ Flash File content-type
    """
    security = ClassSecurityInfo()
    implements(IFlashAnimation)


    # This name appears in the 'add' box
    archetype_name             = 'FlashFile'
    meta_type                  = 'FlashFile'
    portal_type                = 'FlashFile'
    allowed_content_types      = [] + list(getattr(ATFile,
                                                   'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'FlashFile.gif'
    immediate_view             = 'flashfile_view'
    default_view               = 'flashfile_view'
    suppl_views                = ('flashfile_view', 'flashfile_noheader_view',
                                  'flashfile_fixed_width_view',
                                  'flashfile_popup_view', 'base_view')
    typeDescription            = "FlashFile"
    typeDescMsgId              = 'description_edit_flashfile'

    schema = FlashFile_schema

    security.declarePublic('index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ Use the chosen template to display the flash file.
        """
        return self()

registerType(FlashFile, PROJECTNAME)
