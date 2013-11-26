""" Adapters
"""
from Products.CMFCore.utils import getToolByName
from eea.workflow.readiness import ObjectReadiness


infographic_required_for_publishing = ("Data", "EEAFigure",
                                       "ExternalDataSpec", "Report",
                                       "Assesment")


def has_one_of(has, in_list):
    """ Returns True if there is at least one object of type 'has' in the list
        'list' and the object is published
    """
    in_list = in_list or []
    if not in_list:
        return False
    wftool = getToolByName(in_list[0], 'portal_workflow')
    for obj in in_list:
        if wftool.getInfoFor(obj, 'review_state') == 'published' and \
                        obj.portal_type in has:
            return True
    return False

class InfographicWorkflowStateReadiness(ObjectReadiness):
    """ObjectReadiness customizations"""

    checks = {'published': (
        (lambda o: not has_one_of(infographic_required_for_publishing,
                                   o.getRelatedItems()),
         "The Infographic needs to point within the Related Items field to "
         "at least one published %s" % (
             ", ".join(infographic_required_for_publishing))),
    )}

