""" Smart folder views
"""
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from eea.themecentre.utils import localized_time
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import getMultiAdapter

DATE_FIELDS = ('start', 'end', 'EffectiveDate', 'effective', 'expires')


class SmartFolderPortlets(object):
    """ Smart folder portlets
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')

        portal = portal_url.getPortalObject()
        obj = self.context
        while not (INavigationRoot.providedBy(obj) and
                   aq_base(obj) is not aq_base(portal)):
            obj = utils.parent(obj)

        return self.portlets(obj)

    def portlets(self, context):
        """ Portlets
        """
        if self.context.portal_type in ['Topic']:
            # context is a smartfolder so we make only one portlet
            topics = [self.context]
        else:
            topics = self._find_topics(context)
        portlets = []

        for topic in topics:
            portlet = self._portlet_info(topic)
            portlet['entries'] = self._portlet_entries(topic)

            if portlet['entries']:
                portlets.append(portlet)

        if len(portlets) > 1:
            portlets.sort(cmp=lambda x, y: cmp(x['sort_key'], y['sort_key']))

        return portlets

    def _find_topics(self, context):
        """ Find topics
        """
        manually_added_portlets = getattr(context,
                                          'manually_added_portlets', [])
        catalog = getToolByName(context, 'portal_catalog')
        query = { 'portal_type': 'Topic',
                  'review_state' : 'published',
                  'path': '/'.join(context.getPhysicalPath()) }
        brains = catalog.searchResults(query)
        return [brain.getObject() for brain in brains
                if brain.getId not in manually_added_portlets ]

    def _parent_or_topic(self, topic):
        """ Parent or topic
        """
        view = getMultiAdapter((topic, self.request),
                               name="plone_context_state")
        if view.is_default_page():
            parent = aq_parent(aq_inner(topic))
            if parent is None:
                return topic
            else:
                return parent
        else:
            return topic

    def _portlet_entries(self, topic):
        """ Entries
        """
        topic_query = topic.buildQuery()
        catalog = getToolByName(topic, 'portal_catalog')
        entries = []
        if topic_query:
            topic_query['sort_limit'] = 3
            topic_brains = catalog.searchResults(topic_query)
            extra_fields = [ field for field in topic.getCustomViewFields()
                                   if field != 'Title' ]

            for tb in topic_brains:
                item = { 'url': tb.getURL(),
                         'title': tb.Title,
                         'detail': self._detail(extra_fields, tb) }
                entries.append(item)
        return entries

    def _portlet_info(self, topic):
        """ Info
        """
        portlet = {}
        portlet['entries'] = []
        portlet['title'] = self._title(topic)
        portlet['all_link'] = self._parent_or_topic(topic).absolute_url()
        portlet['sort_key'] = self._sort_key(topic)
        portlet['feed_link'] = topic.absolute_url() + '/RSS'
        return portlet

    def _detail(self, extra_fields, brain):
        """ Details
        """
        detail = u''

        for index, field in enumerate(extra_fields):
            if field in DATE_FIELDS:
                time = localized_time(brain[field])
                if (index > 0 and extra_fields[index - 1] in
                    DATE_FIELDS and time):
                    detail += u' - ' + time
                elif detail and time:
                    detail += u', ' + time
                elif time:
                    detail += time
            else:
                if detail:
                    detail += u', '
                if field == 'location':
                    # only date is used for detail therefore we pass the
                    # location
                    continue
                elif isinstance(brain[field], (list, tuple)):
                    detail += ', '.join(value.decode('utf8')
                                        for value in brain[field])
                else:
                    detail += brain[field].decode('utf8')

        return detail

    def _title(self, topic):
        """ Title
        """
        return topic.Title()

    def _sort_key(self, topic):
        """ Sort key
        """
        return topic.getId()

class LatestHighlightsSmartFolderPortlet(SmartFolderPortlets):
    """ Latest highlights smart folder portlet
    """
    def _find_topics(self, context):
        """ Find topics
        """
        catalog = getToolByName(context, 'portal_catalog')
        query = { 'portal_type': 'Topic',
                  'path': '/www/SITE/highlights/archive',
                  'Language': 'en' }
        brains = catalog.searchResults(query)
        return [brain.getObject() for brain in brains]

    def _portlet_entries(self, topic):
        """ Entries
        """
        currentLang = self.context.Language()
        topic_query = topic.buildQuery()
        topic_query['Language'] = 'en'
        catalog = getToolByName(topic, 'portal_catalog')
        topic_brains = catalog.searchResults(topic_query)
        entries = []
        extra_fields = topic.getCustomViewFields()
        for tb in topic_brains:
            if currentLang not in tb.getTranslationLanguages:
                item = { 'url': tb.getURL(),
                         'title': tb.Title,
                         'detail': self._detail(extra_fields, tb) }
                entries.append(item)
                if len(entries) == 5:
                    break
        return entries
