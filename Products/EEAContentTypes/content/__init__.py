""" Content init module """

# Validators
from Products.EEAContentTypes.content import validators

# Classes
from Products.EEAContentTypes.content import Article
from Products.EEAContentTypes.content import CFTRequestor
from Products.EEAContentTypes.content import CallForInterest
from Products.EEAContentTypes.content import CallForTender
from Products.EEAContentTypes.content import infographic
from Products.EEAContentTypes.content import Event
from Products.EEAContentTypes.content import ExternalHighlight
from Products.EEAContentTypes.content import FlashFile
from Products.EEAContentTypes.content import CloudVideo
from Products.EEAContentTypes.content import GISApplication
from Products.EEAContentTypes.content import Highlight
from Products.EEAContentTypes.content import Link
from Products.EEAContentTypes.content import PressRelease
from Products.EEAContentTypes.content import Promotion
from Products.EEAContentTypes.content import Speech
from Products.EEAContentTypes.content import ThemeTaggable


# monkey patch, replaces reference field of certain content types to
# an orderable reference field
from Products.EEAContentTypes.content.orderablereffield import field
from Products.EEAContentTypes.content.orderablereffield import (
    types_and_schema,
)

from Products.Archetypes.ClassGen import generateMethods
for otype, schema in types_and_schema:
    schema.addField(field)
    schema.moveField('relatedItems', pos='bottom')
    generateMethods(otype, [field])

# monkey patch, by default file is not translatable, fix this
from Products.ATContentTypes.content import file as atfile
atfile.ATFileSchema['file'].languageIndependent = False

# #4898 Set Content-Disposition: attachment for PDF files
inlineMimetypes = atfile.ATFile.inlineMimetypes
if 'application/pdf' in inlineMimetypes:
    inlineMimetypes = set(inlineMimetypes)
    inlineMimetypes.remove('application/pdf')
    atfile.ATFile.inlineMimetypes = tuple(inlineMimetypes)

from Products.ATContentTypes.content import image
image.ATImageSchema['rights'].languageIndependent = True

__all__ = [
    ThemeTaggable.__name__,
    Speech.__name__,
    Article.__name__,
    CFTRequestor.__name__,
    CallForInterest.__name__,
    CallForTender.__name__,
    Event.__name__,
    ExternalHighlight.__name__,
    FlashFile.__name__,
    CloudVideo.__name__,
    GISApplication.__name__,
    Highlight.__name__,
    Link.__name__,
    PressRelease.__name__,
    Promotion.__name__,
    validators.__name__,
    infographic.__name__
]
