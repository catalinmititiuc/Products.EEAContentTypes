""" RSS
"""
from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class RSSShare(BrowserView):
    """ RSS Share
    """
    def main(self):
        """ Main
        """
        include = self.request.get('include_channels', None)
        nritems = int(self.request.get('nritems', 10))
        if include is not None:
            try:
                include = include.split(',')
            except Exception:
                include = None

        rssFeeds = RSSFeedsContent(self.context, self.request).getFeeds()
        if include is not None and include != []:
            rssFeeds = [ feed for feed in rssFeeds
                              if feed.getId() in include ]

        ct = getToolByName(self.context, 'portal_catalog')
        query = { 'portal_type' : ('Highlight', 'PressRelease'),
                  'review_state' : 'published',
                  'sort_on' : 'effective',
                  'sort_order' : 'reverse',
                  'effectiveRange' : DateTime() }
        allItems = ct.searchResults(query)[:nritems]

        for feed in rssFeeds:
            feedItems = feed.getFeed()[:nritems]
            for item in feedItems:
                nItem = { 'pretty_title_or_id' : item['Title'],
                          'Identifier' : item['getURL'],
                          'modified' : item['Date'],
                          'Publisher' : '',
                          'Creator' : '',
                          'Rights' : '',
                          'Subject' : [],
                          'Type' : 'RSSItem from RSSRecipe',
                          }
                nItem.update(item)
                allItems.append(nItem)

        return allItems

class RSSFeedsContent(BrowserView):
    """ RSS Feeds content
    """
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.rssFolder = getattr(context, 'rss')

    def getFeeds(self):
        """ Feeds getter
        """
        return []

    def getDblFeeds(self):
        """ Dbl feeds getter
        """
        size = 2
        feedList = self.getFeeds()
        return [feedList[i:i + size] for i in range(0, len(feedList), size)]


class RSSFeeds(BrowserView):
    """ RSS Feeds
    """
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.rssFolder = getattr(context, 'rss')

    def getFeeds(self):
        """ Feeds getter
        """
        return []

    def getDblFeeds(self):
        """ Dbl feeds getter
        """
        size = 2
        feedList = self.getFeeds()
        return [feedList[i:i + size] for i in range(0, len(feedList), size)]
