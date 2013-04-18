"""Plugins to modify @@rdf info
"""

from Products.Archetypes.interfaces import IField
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from eea.rdfmarshaller.interfaces import ISurfSession
from eea.versions.interfaces import IVersionEnhanced, IGetVersions
from zope.component import adapts
from zope.interface import implements, Interface
import rdflib


class VersioningModifier(object):
    """Adds information about versioning
    """

    implements(ISurfResourceModifier)
    adapts(IVersionEnhanced)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """change the rdf resource
        """
        api = IGetVersions(self.context)

        newer = api.later_versions()
        older = api.earlier_versions()
        resource.dcterms_isReplacedBy = [rdflib.URIRef(i['url']) for
                                                        i in newer]
        resource.dcterms_replaces = [rdflib.URIRef(a['url']) for a in older]

        resource.save()

        
class MediaField2Surf(ATField2Surf):
    """A mediafield to surf adapter for the "media" field
    """
    adapts(IField, Interface, ISurfSession)

    def value(self):
        """Tranform value to surf value
        """
        f = self.context.getMedia()
        if not len(f):
            return None

        return [rdflib.URIRef(f.absolute_url()+"/image_xlarge")]

