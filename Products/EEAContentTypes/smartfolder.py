from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.criteria.base import ATBaseCriterion

def smartFolderAdded(obj, evt):
    portal = getToolByName(obj, 'portal_url').getPortalObject()
    portal_types = getToolByName(obj, 'portal_types')

    
    # get the translated object by taking the first part of the url
    canonical = obj.getCanonical()
    obj = evt.target
    copyids = []

    for object in canonical.objectValues():

        if isinstance(object, ATBaseCriterion):
            # copy the criteria over to the new translated smart folder

            # save content type restrictions and change them temporarily
            # so we are allowed to add criteria objects to the smart folder
            # by default only smart folders can be added to smart folders

            crit_type = getattr(portal_types, object.portal_type)
            topic_type = getattr(portal_types, obj.portal_type)
            global_allow = crit_type.global_allow
            filter = topic_type.filter_content_types

            crit_type.global_allow = True
            topic_type.filter_content_types = False
            copy = canonical.manage_copyObjects([object.getId()])
            obj.manage_pasteObjects(copy)

            # restore the original restrictions
            crit_type.global_allow = global_allow
            topic_type.filter_content_types = filter
