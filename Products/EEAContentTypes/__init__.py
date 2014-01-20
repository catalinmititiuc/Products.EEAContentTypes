# -*- coding: utf-8 -*-
""" EEA Content Types
"""

from Products.ATContentTypes.content import event, topic
from Products.ATContentTypes.content.schemata import marshall_register
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.CMFCore import utils as cmfutils
from Products.EEAContentTypes.config import ADD_CONTENT_PERMISSIONS
from Products.EEAContentTypes.config import DEFAULT_ADD_CONTENT_PERMISSION
from Products.EEAContentTypes.config import PROJECTNAME
import logging
logger = logging.getLogger('Products.EEAContentTypes')


#import patches
#TODO: complete migration to plone4 for the patches


def finalizeSchema(schema, disableRelated=False, moveDiscussion=True,
                   moveThemeTag=True):
    """Finalizes an ATCT type schema to alter some fields
    """
    schema.moveField('relatedItems', pos='bottom')
    if disableRelated:
        schema['relatedItems'].widget.visible['edit'] = 'invisible'
    else:
        schema['relatedItems'].widget.visible['edit'] = 'visible'
        schema.moveField('relatedItems', after='text')

    # if moveThemeTag:
    #     schema.moveField('themes', before='relatedItems')

    if moveDiscussion:
        schema['allowDiscussion'].schemata = 'metadata'
        schema.moveField('allowDiscussion', after='relatedItems')

    marshall_register(schema)
    return schema


def setupSchemas():
    """ Setup schema
    """
    from Products.EEAContentTypes.content import (
        Promotion,
        PressRelease,
        Highlight,
        CallForInterest,
        CallForTender,
        CFTRequestor,
        Event
    )
    # (schema, moveDiscussion, disableRelated, moveThemeTag)
    types = ( (Promotion.Promotion_schema, True, False, True),
              (PressRelease.PressRelease_schema, True, False, True),
              (Highlight.Highlight_schema, False, False, True),
              (event.ATEvent.schema, True, True, False),
              (Event.QuickEvent.schema, True, True, False),
              (CallForInterest.CallForInterest_schema, True, True, False),
              (CallForTender.CallForTender_schema, True, True, False),
              (CFTRequestor.CFTRequestor_schema, True, True, False),)
    for schema, moveDiscussion, disableRelated, moveThemeTag in types:
        finalizeSchema(schema, moveDiscussion=moveDiscussion,
                       disableRelated=disableRelated, moveThemeTag=moveThemeTag)

    topic.ATTopicSchema['acquireCriteria'].widget.condition = (
        "python:folder.getParentNode().portal_type in ['Topic']")


def initialize(context):
    """ Zope 2
    """

    # imports packages and types for registration
    from Products.EEAContentTypes import content
    content.__name__

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0, len(all_content_types)):
        klassname = all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])

    setupSchemas()
