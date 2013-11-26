""" Definition of the Infographic content type
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType

from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content import image
from Products.EEAContentTypes.config import EEAMessageFactory as _, PROJECTNAME

from plone.app.blob import field
from Products.EEAContentTypes.content.interfaces import IInfographic


SCHEMA = atapi.Schema((

    field.ImageField(
        name="image",
        schemata="default",
        sizes=None,
        required=True,
        primary=True,
        widget=field.ImageWidget(
            label=_("Infographic"),
            description=_("Infographic image"),
            i18n_domain='eea',
        )
    ),

    atapi.StringField(
        name='imageCopyright',
        schemata="default",
        widget=atapi.StringWidget(
            label=_("Image Copyright"),
            description=_("Enter the copyright information for this image."),
            i18n_domain='eea',
        )
    ),

    atapi.TextField(
        name='license',
        schemata="creators",
        allowable_content_types=('text/plain',),
        widget=atapi.TextAreaWidget(
            label=_(u'License'),
            description=_(u'License information')
        )
    ),
    atapi.TextField(
        name='publisher',
        schemata="creators",
        allowable_content_types=('text/plain',),
        widget=atapi.TextAreaWidget(
            label=_(u'Publisher'),
            description=_(u'Publisher information')
        )
    ),
    atapi.BooleanField(
        schemata='settings',
        name='presentation',
        required=False,
        languageIndependent=True,
        widget=atapi.BooleanWidget(
            label=_(u'Presentation mode'),
            description=_(u"If selected, this will give users the ability to "
                          u"view the contents as presentation slides.")
        )
    )
))



class Infographic(image.ATImage):
    """ Infographic """

    implements(IInfographic)

    meta_type = "Infographic"
    portal_type = "Infographic"
    archetypes_name = "Infographic"

    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    schema = (
        image.ATImageSchema.copy() +
        SCHEMA.copy()
    )
    schema["title"].required = True


registerType(Infographic, PROJECTNAME)
