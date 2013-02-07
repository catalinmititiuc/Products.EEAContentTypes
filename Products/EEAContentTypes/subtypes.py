""" Subtypes
"""
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import ISchema
from Products.EEAContentTypes.config import REQUIRED_METADATA_FOR
from Products.LinguaPlone.public import InAndOutWidget
from Products.LinguaPlone.public import StringField
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from eea.geotags import field
from eea.geotags import widget
from eea.themecentre.content.ThemeTaggable import ThemesField
from p4a.subtyper.engine import Subtyper as BaseSubtyper, DescriptorWithName
from p4a.subtyper.interfaces import IPortalTypedPossibleDescriptors
from p4a.subtyper.interfaces import IPossibleDescriptors
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import provider
from p4a.videoembed.utils import break_url
from zope.component import adapts
from zope.component import queryAdapter
from zope.interface import Interface, implements
from p4a.video.subtype import TopicVideoContainerDescriptor as \
        BaseTopicVideoContainerDescriptor, _
from eea.relations.field import EEAReferenceField
from eea.relations.widget import EEAReferenceBrowserWidget
from eea.relations.interfaces import IAutoRelations
from eea.relations.component import getForwardRelationWith
from eea.relations.component import getBackwardRelationWith

import logging

logger = logging.getLogger('EEAContentTypes')

class ExtensionRelationsField(ExtensionField, EEAReferenceField):
    """ derivative of relations for extending schemas """

class ExtensionStringField(ExtensionField, StringField):
    """ derivative of stringfield for extending schemas """

class ExtensionGeotagsSinglefield(ExtensionField, field.GeotagsStringField):
    """ derivative of blobfield for extending schemas """

class ExtensionGeotagsMultifield(ExtensionField, field.GeotagsLinesField):
    """ derivative of blobfield for extending schemas """

class ExtensionThemesField(ExtensionField, ThemesField):
    """ derivative of themesfield for extending schemas """

class RelationsSchemaExtender(object):
    """ Extends relations filed
    """
    implements(ISchemaExtender)

    fields = (
     ExtensionRelationsField('relatedItems',
        schemata='categorization',
        relationship = 'relatesTo',
        multiValued = True,
        languageIndependent=True,        
        keepReferencesOnCopy=True,
        widget=EEAReferenceBrowserWidget(
            label='Related items',
            description='Specify relations to other content within Plone.'
        )
      ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Returns relatedItems field
        """
        # List of content types where relatedItems field
        # is override in specific schemata
        if self.context.portal_type in (
            "DavizVisualization", "Specification", "Assessment",
            "AssessmentPart", "QuickEvent", "Report", "IndicatorFactSheet"):
            return []

        # Due to #4705 base_view shows related widget which should be
        # rendered by the macro from main_template
        if self.context.portal_type in ("Promotion",):
            self.fields[0].widget.visible['view'] = 'invisible'

        return self.fields

class LocationSchemaExtender(object):
    """ Extends base schema with extra fields.
        To be used for base content class.
    """
    implements(ISchemaExtender)

    multiple_location =  (
        ExtensionGeotagsMultifield(
            name='location',
            schemata='categorization',
            required=False,
            languageIndependent=True,
            widget=widget.GeotagsWidget(
                label='Geotags / Locations',
                description=('Geotags: multiple geographical locations '
                             'related to this content. Click Edit button '
                             'to select a location')
                )
            ),
        )

    single_location = (
        ExtensionGeotagsSinglefield(
            name='location',
            schemata='categorization',
            required=False,
            languageIndependent=True,
            widget=widget.GeotagsWidget(
                label='Geotag / Location',
                description=('Geotags: geographical location '
                             'related to this content. Click Edit button '
                             'to select a location')
                )
            ),
        )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        # quickevents has all information on the default editing form
        if getattr(self.context, 'portal_type', None) == 'QuickEvent':
            self.multiple_location[0].schemata = 'default'
            self.multiple_location[0].widget.label = 'Event Location'
            self.multiple_location[0].widget.label_msgid = \
                                                    "label_event_location"
            self.multiple_location[0].widget.description = \
                             'Geographical location ' \
                             'related to this Event. Click Edit button' \
                             ' to select a location'
            self.multiple_location[0].widget.description_msgid = (
                            'EEAContentTypes_help_location_event')
            return self.multiple_location
        # likewise Organisation had the previous location widget on default
        elif getattr(self.context, 'portal_type', None) == 'Organisation':
            self.multiple_location[0].schemata = 'default'
            self.multiple_location[0].widget.label = "Organisation Address"
            self.multiple_location[0].widget.label_msgid = \
                                                    "dataservice_label_address"
            self.multiple_location[0].widget.description = (
                             'Geographical location ' \
                             'related to this Organisation. Click Edit button' \
                             ' to select a location')
            self.multiple_location[0].widget.description_msgid = \
                                                    "dataservice_help_address"
            return self.multiple_location
        # #9423 remove location schema extender for Data 
        elif self.context.portal_type == 'Data':
            return ()
        else:
            self.multiple_location[0].schemata = 'categorization'
            self.multiple_location[0].widget.label = "Geotag / Location"
            self.multiple_location[0].widget.description = (
                             'Geotags: geographical location '
                             'related to this content. Click Edit button '
                             'to select a location')
            return self.multiple_location

class ThemesSchemaExtender(object):
    """ Extends schema with themes field
    """
    implements(ISchemaExtender)

    fields = (
        ExtensionThemesField(
            name='themes',
            schemata='categorization',
            validators=('maxValues',),
            required=False,
            widget=InAndOutWidget(
                maxValues=3,
                label="Themes",
                description="Choose max 3 themes",
                ),
            languageIndependent=True,
            vocabulary_factory=u"Allowed themes for edit",
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        if getattr(self.context, 'portal_type', None) in ('QuickEvent',):
            # No schema extender for QuickEvent
            return []
        return self.fields

class RequiredSchemaModifier(object):
    """ Modify schema
    """
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        getCanonical = getattr(self.context, 'getCanonical', None)
        if getCanonical:
            try:
                canonical = getCanonical()
            except Exception, err:
                logger.debug(err)
            else:
                if self.context != canonical:
                    # Language independent doesn't work with required property
                    return

        if 'location' in schema and self.context.portal_type != 'Data':
            xfield = schema['location']
            xfield.required = True
        if 'themes' in schema:
            xfield = schema['themes']
            xfield.required = True
        if 'subject' in schema:
            xfield = schema['subject']
            xfield.required = True


class KeywordsSchemaModifier(object):
    """ Fix keywords postback bug http://dev.plone.org/ticket/12334
    """
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        if 'subject' in schema:
            # since only subject has the keywordsWidget macro we can disable
            # giving it eea_keywords since eea.tags as it's own keywords macro
            # schema['subject'].widget.macro = 'eea_keywords'
            # TODO: this fix doesn't apply to this problem anymore,
            # to be removed or to be replaced if a keywordsWidget field is
            # added

            # make subject field languageIndependent as required since ticket
            # 8761
            schema['subject'].languageIndependent = True


class RequiredByPortalTypeSchemaModifier(RequiredSchemaModifier):
    """ Modify schema
    """
    implements(ISchemaModifier)

    def fiddle(self, schema):
        """ Fields
        """
        portal_type = getattr(self.context, 'portal_type', '')
        if portal_type not in REQUIRED_METADATA_FOR:
            return
        return super(RequiredByPortalTypeSchemaModifier, self).fiddle(schema)

class GeotagMixinEdit(object):
    """ Edit
    """
    adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    @property
    def geotag(self):
        """ Getter
        """
        schema = ISchema(self.context)
        xfield = schema['location']
        accessor = xfield.getAccessor(self.context)
        return accessor()

    @geotag.setter
    def geotag(self, value):
        """ Setter
        """
        schema = ISchema(self.context)
        xfield = schema['location']
        mutator = xfield.getMutator(self.context)
        mutator(value)

class IGeotagSingleEdit(Interface):
    """ Interface for editing single location
    """
    geotag = widget.location.GeotagSingleField(
            title = u"Geotag",
            description=(u"Geotag: a single geographical location for "
                         "this content.")
            )

class GeotagSingleEdit(GeotagMixinEdit):
    """ Single edit
    """
    implements(IGeotagSingleEdit)

class IGeotagMultiEdit(Interface):
    """ Interface for editing multiple locations
    """
    geotag = widget.location.GeotagMultiField(
            title = u"Geotags",
            description=(u"Geotags: multiple geographical locations related to"
                         " this content.")
            )

class GeotagMultiEdit(GeotagMixinEdit):
    """ Multi Edit
    """
    implements(IGeotagMultiEdit)

class Subtyper(BaseSubtyper):
    """ We override the default subtyper because of broken logic in its
        possible_types implementation. The default implementation, due to
        adapter resolution order, doesn't take into account adapters for
        IPortalTypedPossibleDescriptors

        Also, not it's possible to hide the menu for content types where
        it doesn't make sense. This is due to the fact that the subtyper
        in p4a.video is registered for somewhat generic interfaces
        (for ex: IATFolder)
    """
    _skip = ('Data', 'EEAFigure')

    def possible_types(self, obj):
        """ Possible types
        """
        if obj.portal_type in self._skip:
            return []

        possible = queryAdapter(obj, IPortalTypedPossibleDescriptors)
        if possible and possible.possible:
            return (DescriptorWithName(n, c) for n, c in possible.possible)

        possible = IPossibleDescriptors(obj)
        return (DescriptorWithName(n, c) for n, c in possible.possible)

class TopicVideoContainerDescriptor(BaseTopicVideoContainerDescriptor):
    """ Topic container
    """
    title = _("Video Topic Container")

@provider(IURLChecker)
def swf_check(url):
    """ Customized utility to check for swf in URL just so
        that we don't transform GIS Applications into videos
    """
    host, path, query, fragment = break_url(url)
    # TODO: plone4 this return false shouldn't be here
    # or the rules after it should be deleted
    return False

    if "discomap.eea.europa.eu" in host and 'index.swf' in path:
        return False

    if path.endswith('.swf'):
        return True

    return False

swf_check.index = 10100

class GetCanonicalRelations(object):
    """ Reproduce the relations of the canonical object, 
        In our case, the canonicals should all be in EN.
    """

    implements(IAutoRelations)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        tabs = {}

        if self.context.isCanonical():
            # Canonical object, we return nothing
            return None
        else: 
            lang = self.context.Language()
            canonical = self.context.getCanonical()
            # Get canonical relations forward and backward. 
            # As translations are related to the canonical object,
            # we specify the parameters in the backward not to list them. 
            
            # Used in relations/browser/app/macro.py, but doesn't work 
            # when there are no relations on the object
            #
            # fieldname = kwargs.get('fieldname', 'relatedItems')
            # field = canonical.getField(fieldname)
            # if field:
            #    accessor = field.getAccessor(self.context)
            #    rel_forwards = accessor()            
            
            rel_forwards = canonical.getRefs(kwargs.get('relation',
                                                          'relatesTo'))
            if rel_forwards:
                # Get translations of forward relations, if 
                # translations don't exist, return canonical
                
                for relation in rel_forwards:
                    # Get the relation type name                  
          
                    forward = getForwardRelationWith(self.context, relation)
                    if not forward:
                        continue
                      
                    name = forward.getField('forward_label').getAccessor(
                                                             forward)()

                    if name not in tabs:
                        tabs[name] = []                    
                    
                    if relation.getTranslation(lang):
                        tabs[name].append(relation.getTranslation(lang)) 
                    else:
                        tabs[name].append(relation)
            
            rel_backwards = canonical.getBRefs(kwargs.get('relation',
                                                          'relatesTo'))
            if rel_backwards:
                # Get translations of backward relations, if 
                # translations don't exist, return canonical
                
                for relation in rel_backwards:
                    # Get the relation type name
                    # if not self.checkPermission(relation):
                    #    continue
        
                    backward = getBackwardRelationWith(self.context, relation)
                    if not backward:
                        continue
                    name = backward.getField('backward_label').getAccessor(
                                                               backward)()
    
                    if name not in tabs:
                        tabs[name] = []
         
                    if relation.getTranslation(lang):
                        tabs[name].append(relation.getTranslation(lang))
                    else:
                        tabs[name].append(relation)

            if tabs:
                return tabs.items()
            else:
                return None

