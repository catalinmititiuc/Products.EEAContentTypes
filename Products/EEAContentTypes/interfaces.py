""" Interfaces
"""
from zope.interface import Interface, Attribute

class IEEAPloneSite(Interface):
    """A marker interface for the EEA Plone site
    """


class IFeedPortletInfo(Interface):
    """ Any object that wants to be displayed in a themecentre portlet
        should provide an adapter providing this interface. """

    feed_id = Attribute("feed id")
    title = Attribute("portlet title")
    title_link = Attribute("portlet title link")
    button_link = Attribute("feed button link")
    more_link = Attribute("portlet more link")
    items = Attribute("a list of portlet items")


class IFeedItemPortletInfo(Interface):
    """ Each item in the themecentre portlets provides this interface. """

    title = Attribute("portlet item title")
    description = Attribute("portlet item description")
    url = Attribute("portlet item link")
    detail = Attribute("portlet item detail")
    image = Attribute("portlet item image")
    coverage = Attribute("portlet coverage")
    published = Attribute("published date")
    summary = Attribute("feed item summary")


class ITransitionLogicalGuard(Interface):
    """ Transition logical guard
    """
    available = Attribute("boolean if transitions is available")


class ILocalRoleEmails(Interface):
    """ Local role emails
    """
    emails = Attribute("Dictionary with emails for each role")


class IRelations(Interface):
    """ An adapter that retrieves relations from any plone object. """

    def all(samePortalType=False):
        """ Gets all objects that are, in any way, related to this object. """

    def backReferences():
        """ Gets all objects that have references to this object. """

    def backReferencesWithSameType(self):
        """ Gets all objects that have references to this object,
        and are the same portal_type.
        """

    def forwardReferences():
        """ Gets all objects that this object has references to. """

    def autoContextReferences():
        """ Gets all objects that are referenced from this objects
        backreferences.
        """

    def byTheme(samePortalType=False, getBrains=False, constraints=False):
        """ Gets all objects that have the same theme tag is the adapted object.
            samePortalType argument should be true if the related objects should
            be of the same portal type as context. getBrains argument should be
            true if one only wants the brains back instead of the whole objects.
            This is mainly for performance. """

    def byPublicationGroup(samePortalType=True, getBrains=False):
        """ Get all objects that are the same type and same publication group.
        """

    def references():
        """" Gets both forward and backward references. """

class IRequiredFields(Interface):
    """ Marker interface for Content-Types that should have required metadata
    like: subject, location, themes
    """
