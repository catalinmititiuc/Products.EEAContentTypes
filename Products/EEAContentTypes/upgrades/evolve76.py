""" evolve script
"""
import logging
from Products.CMFCore.WorkflowCore import WorkflowException

logger = logging.getLogger('Products.EEAContentTypes.migration')


def evolve(context):
    """ Reindex SOERKeyFact's after removing workflow defined for it and
        publish their parents if they are not
    """

    logger.info("Starting reindex of SOERKeyFact objects")
    cat = context.portal_catalog
    brains = cat.searchResults(portal_type="SOERKeyFact", Language="all")
    wftool = context.portal_workflow

    for brain in brains:
        obj = brain.getObject()
        try:
            obj.reindexObject()
        except Exception:
            msg = "Couldn't reindex %s" % (obj.absolute_url())
            logger.info(msg)
        parent = obj.aq_parent
        # check if parent isn't published and is of type Folder
        if wftool.getInfoFor(parent, 'review_state') != "published" and \
                parent.portal_type == "Folder":
            try:
                wftool.doActionFor(parent, 'publish')
            except WorkflowException:
                msg = "Couldn't publish the parent %s of %s" % (
                    parent.absolute_url(), obj.absolute_url())
                logger.warn(msg)

    logger.info("Finished reindex of SOERKeyFacts and publishing of parents")
