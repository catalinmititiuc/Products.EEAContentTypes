""" evolve script
"""
import logging

logger = logging.getLogger('Products.EEAContentTypes.migration')


def evolve(context):
    """ Reindex SOERKeyFact's after removing workflow defined for it
    """

    logger.info("Starting reindex of SOERKeyFact objects")
    cat = context.portal_catalog
    brains = cat.searchResults(portal_type="SOERKeyFact", Language="all")

    for brain in brains:
        obj = brain.getObject()
        try:
            obj.reindexObject()
        except Exception:
            msg = "Couldn't reindex %s" % (obj.absolute_url())
            logger.info(msg)

    logger.info("Finished reindex of SOERKeyFact objects")
