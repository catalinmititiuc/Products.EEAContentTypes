""" Upgrade to version 6.6
"""
import logging
import os
import csv
from StringIO import StringIO
from zope.component.hooks import getSite
from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("Products.EEAContentTypes.upgrades")

def cleanup_viewlets(context):
    """ Remove deprecated viewlets
    """
    site = getSite()
    storage = getUtility(IViewletSettingsStorage)
    skins = (u"EEADesign2006", u"EEADesignCMS")
    manager = u"plone.belowcontentbody"
    for skin in skins:
        hidden = storage.getHidden(manager, skin)
        if u"eea.related_multimedia" in hidden:
            hidden = [viewlet for viewlet in hidden
                      if viewlet != u"eea.related_multimedia"]

            logger.info("Cleanup 'eea.related_multimedia' viewlet "
                        "from hidden: %s -- %s -- %s", skin, manager, hidden)
            storage.setHidden(manager, skin, hidden)

        order = storage.getOrder(manager, skin)
        if u"eea.related_multimedia" in order:
            order = [viewlet for viewlet in hidden
                     if viewlet != u"eea.related_multimedia"]
            logger.info("Cleanup 'eea.related_multimedia' viewlet "
                        "from order: %s -- %s -- %s", skin, manager, hidden)
            storage.setOrder(manager, skin, order)

def update_tags(context):
    """ Update existing tags based on #14383
    """
    logger.info("Upgrade step: starting updating all tags from the portal!")
    ctool = getToolByName(context, 'portal_catalog')

    # Read CSV data
    data_filename = 'tags_edited_plural.csv'
    file_path = os.path.join(os.path.dirname(__file__), data_filename)
    file_ob = open(file_path, 'rb')
    file_data = file_ob.read()

    # Parse CSV data

    # CSV columns:
    # "label","gemeturi","glossaryuri","comments","replacewith",
    # "geonames","instructions"
    file_data = StringIO(file_data)
    file_data.seek(0)
    reader = csv.reader(file_data)
    csv_data = []
    for index, row in enumerate(reader):
        csv_data.append(row)

    tags_to_update = {}
    tags_to_delete = {}
    for k in csv_data:
        if k[4] == 'none':
            tags_to_delete[k[0]] = k[4]
        elif k[4]:
            tags_to_update[k[0]] = k[4].strip()
        else:
            pass

    # Update tags
    count = 1

    ### Delete tags
    for tag in tags_to_delete:
        brains = ctool.unrestrictedSearchResults(Subject=tag)
        for brain in brains:
            obj = brain.getObject()
            current_tags = obj.Subject()

    ### Replace tags
    for tag in tags_to_update:
        brains = ctool.unrestrictedSearchResults(Subject=tag)

    logger.info("Upgrade step: done updating all tags from the portal!")
    return ""


