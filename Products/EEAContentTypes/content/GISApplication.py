""" GisApplication Content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import Schema, registerType
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IGISMapApplication
from Products.validation import V_REQUIRED
from zope.interface import implements


schema = Schema((
               StringField(name="arcgis_url", 
                           widget=StringField._properties['widget']( 
                           label="ArcGIS/EyeOnEarth url", 
                           description='Enter the full web address ' \
                      'for Eye on Earth map, ArcGIS map etc...'
                           ), 
                           required=False, 
                           schemata="default", 
                           validators=('isURL',),
               ), 
    
               ImageField('image',
                    required=True,
                    languageIndependent=True,
                    storage = AnnotationStorage(migrate=True),
                    swallowResizeExceptions = \
                                    zconf.swallowImageResizeExceptions.enable,
                    pil_quality = zconf.pil_config.quality,
                    pil_resize_algo = zconf.pil_config.resize_algo,
                    max_size = zconf.ATImage.max_image_dimension,
                    sizes= {'large'   : (768, 768),
                            'preview' : (400, 400),
                            'mini'    : (200, 200),
                            'thumb'   : (128, 128),
                            'tile'    :  (64, 64),
                            'icon'    :  (32, 32),
                            'listing' :  (16, 16),
                           },
                    validators = (('isNonEmptyFile', V_REQUIRED),
                                  ('imageMinSize', V_REQUIRED)),
                    widget = ImageWidget(
                             description = 'High-res preview image'
                                           ' (at least 1024px width)',
                             label= 'Preview image',
                             show_content_type = False,)
                    ),
                      
    ))

GIS_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema.copy()


#Schema overwrites

GIS_schema['description'].required = True #required to increase findability.
GIS_schema['remoteUrl'].required = False
GIS_schema['remoteUrl'].widget.label = 'Flash/Flex GIS application url'
GIS_schema['remoteUrl'].widget.description = 'Enter address to a flash/flex '\
          'application usually ending with .swf'


class GISMapApplication(ATLink):
    """ GisApplication contenttype
    """
    security = ClassSecurityInfo()
    schema = GIS_schema
    implements(IGISMapApplication)

    # This name appears in the 'add' box
    archetype_name = 'GIS Application'
    portal_type = 'GIS Application'

    meta_type = 'GISMapApplication'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = 0
    immediate_view = 'gis_view'
    default_view = 'gis_view'
    typeDescription = "GIS Map Application"
    typeDescMsgId = 'description_edit_gismapapplication'

    _at_rename_after_creation = True
    
    
    def getArcGisUID(self):
        """extract and return arcgis id from the arcgis url if exists otherwise
           return None.
        """
        idx = 0
        uid = None
        if hasattr(self,'arcgis_url'):
            idx = self.arcgis_url.rfind('?webmap=')
        else:
            return None
        if idx > 0 :
            uid = self.arcgis_url[idx+8:]
            
        return uid

registerType(GISMapApplication, PROJECTNAME)
