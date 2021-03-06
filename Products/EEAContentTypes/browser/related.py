""" Related
"""
import logging

from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.browser.interfaces import (
    IDocumentRelated, IAutoRelated
)
from Products.EEAContentTypes.interfaces import IRelations
from Products.Five.browser import BrowserView
from eea.mediacentre.interfaces import IMediaType
from eea.mediacentre.interfaces import IVideo as MIVideo, IMediaPlayer
from eea.themecentre.interfaces import IThemeMoreLink
from eea.themecentre.interfaces import IThemeTagging
from eea.translations import _
from zope.component import (
    queryAdapter, getUtility,
    getMultiAdapter, queryMultiAdapter
)
from zope.schema.interfaces import IVocabularyFactory

logger = logging.getLogger('EEAContentTypes.browser.related')

TOP_VIDEOS = 3
MEDIA_ORDER = ['video']


def getObjectInfo(item, request):
    """ Object info
    """
    plone_utils = getToolByName(item, 'plone_utils')
    wf_tool = getToolByName(item, 'portal_workflow')
    state = getMultiAdapter((item, request), name="plone_context_state")

    item_type_class = plone_utils.normalizeString(item.portal_type)
    item_wf_state = wf_tool.getInfoFor(item, 'review_state', '')
    item_wf_state_class = 'state-' + plone_utils.normalizeString(item_wf_state)
    url = state.view_url()
    mimetype = item.get_content_type()
    imgview = queryMultiAdapter((item, request), name='imgview')
    info = {'title': item.Title(),
            'uid': item.UID(),
            'description': item.Description(),
            'url': url,
            'absolute_url': item.absolute_url(),
            'has_img': imgview != None and imgview.display() is True,
            'is_video': MIVideo.providedBy(item),
            'item_type': item.portal_type,
            'item_mimetype': mimetype,
            'item_type_class': item_type_class,
            'item_wf_state': item_wf_state,
            'item_wf_state_class': item_wf_state_class}

    return info


def getBrainInfo(brain, plone_utils, typesUsingViewUrl=None):
    """ Brain info
    """
    url = brain.getURL()
    info = {'title': brain.Title,
            'brain': brain,
            'uid': brain.UID,
            'description': brain.Description,
            'absolute_url': url,
            'url': url,
            'is_video':
                "eea.mediacentre.interfaces.IVideo" in brain.object_provides,
            'item_type': brain.portal_type,
            'item_type_class': plone_utils.normalizeString(brain.portal_type),
            'item_wf_state': brain.review_state,
            'item_wf_state_class':
                'state-' + plone_utils.normalizeString(brain.review_state)

            # these infos are missing when compared to full info
            # 'url': brain.getURL() + "/view",
            # 'item_mimetype':mimetype,
            # 'has_img': imgview != None and imgview.display() == True,

            }

    # 13771 set /view to info dict without waking up object with
    # annotatedBrainInfo by checking directly on brain if item_type is in the
    # typesUsingViewUrl
    if typesUsingViewUrl and info['item_type'] in typesUsingViewUrl:
        info['url'] = url + '/view'

    return info


def annotateBrainInfo(info, request, urlOnly=None):
    """Adds details about the object taken from its brain

    Note on the optimization that this achieves:
    There are a couple of cases where there are a lot of results
    (for example from a catalog search of "same theme") that are
    trimmed down to a couple of objects. We don't want to compute
    getObjectInfo for each, because that's expensive.
    Instead we first call getBrainInfo for each brain, trim the
    result and then call annotateBrainInfo for each brain.
    """

    if info.get('brain'):
        brain = info['brain']
        obj = brain.getObject()
        state = getMultiAdapter((obj, request), name="plone_context_state")
        url = state.view_url()
        if not urlOnly:
            imgview = queryMultiAdapter((obj, request), name="imgview")
            info['has_img'] = (imgview is not None and imgview.display()
                               is True)
            info['item_mimetype'] = obj.get_content_type()
        info['url'] = url


def annotateByThemeInfo(byTheme, request):
    """Add extra information that can only be retrieved from the full object
       In the case of themes we need only the url
    """

    for _theme, infos in byTheme.items():
        for info in infos:
            annotateBrainInfo(info, request, urlOnly=True)


def annotateThemeInfos(themeinfos, request):
    """ Brain info
    """
    for info in themeinfos:
        annotateBrainInfo(info, request)


def filterDuplicates(items):
    """ filter duplicates by overriding uid keys with latest dict value
    """
    uids = {}
    for i in items:
        uids[i['uid']] = i
    return uids.values()

    # uids = []
    # ret = []
    # for i in items:
    # if i['uid'] not in uids:
    # uids.append(i['uid'])
    # ret.append(i)
    # return ret


def others(context, brains):
    """Returns a list of brains which do no point to the context
    """
    plone_utils = getToolByName(context, 'plone_utils')
    cid = context.getId()
    return [getBrainInfo(b, plone_utils) for b in brains if b.getId != cid]


class AutoRelated(object):
    """ Auto related
    """
    implements(IAutoRelated)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sameTypeByTheme(self, constraints=None):
        """NOTE: returns full info. The results are limited in number so
        we can afford this
        :param constraints: a dict which constraints the result of the query
        """
        # doesn't return latest item found at
        # www/SITE/themes/natural/publications
        # which was www/SITE/publications/consumption-and-the-environment-2012
        defaultConstraints = {'review_state': 'published', 'sort_limit': 3,
                              'queryThemesSeparately': True}
        if constraints:
            defaultConstraints.update(constraints)
        limitResults = defaultConstraints['sort_limit']
        result = self.sameTheme(portal_type=self.context.portal_type,
                                constraints=defaultConstraints)
        byTheme = {}

        brainsWithMultipleThemes = []
        for annotatedBrain in result:
            themes = annotatedBrain['commonThemesIds']
            if themes:
                theme = themes[0]
                themeObjs = byTheme.get(theme, [])
                # save items with multiple themes in case we will need them
                # later if we have less results per theme
                if len(themes) > 1:
                    brainsWithMultipleThemes.append(annotatedBrain)

                if len(themeObjs) < limitResults:
                    themeObjs.append(annotatedBrain)
                    byTheme[theme] = themeObjs

        # check if we have the right amount of items based on limitResults
        # for every theme
        for theme in byTheme:
            if len(byTheme[theme]) < limitResults:
                for annotatedBrain in brainsWithMultipleThemes:
                    if theme in annotatedBrain['commonThemesIds']:
                        byTheme[theme].append(annotatedBrain)
                    # break if we already have enough results for the given
                    # theme
                    if not len(byTheme[theme]) < limitResults:
                        break

        # now we have the themes in a dictionary, put them in a list instead
        themes = []
        vocabFactory = getUtility(IVocabularyFactory, name="Allowed themes")
        themesVocab = vocabFactory(self)
        contextThemes = self._contextThemes()
        for themename in contextThemes:
            theme = byTheme.get(themename, None)
            if theme:
                # disabled as auto relation macro from document_relateditems
                # is no longer used on account of pour performance see ticket
                # http://taskman.eionet.europa.eu/issues/7452
                # disabled as part of ticket #13771
                # and added back as part of ticket #13994
                url = IThemeMoreLink(self.context).url(themename)
                try:
                    themeTitle = themesVocab.getTerm(themename).title
                except LookupError:
                    logger.error('unable to retrieve theme name %s from %s',
                                 themename, self.context.absolute_url())
                    continue
                themes.append({'name': _(
                    str(themeTitle)),
                    'items': theme,
                    'more_link': url})

        for dicts in themes:
            # 9272 reverse sort of latest addition
            dicts['items'].reverse()
        return themes

    def sameTheme(self, portal_type=None, constraints=None):
        """
        NOTE: returns incomplete info, from getBrainInfo. You need to call
        annotateBrainInfo() if you need full info

        TODO: this should be made a private methods, not callable through
        the normal API, to emphasize that it doesn't return full info.
        """
        defaultConstraints = {'review_state': 'published'}
        if constraints:
            defaultConstraints.update(constraints)

        result = IRelations(self.context).byTheme(
            portal_type=portal_type,
            getBrains=True,
            considerDeprecated=True,
            constraints=defaultConstraints)

        contextThemes = self._contextThemes()
        related = []
        plone_utils = getToolByName(self.context, 'plone_utils')
        portal_properties = getToolByName(self.context, 'portal_properties',
                                          None)
        site_properties = getattr(portal_properties, 'site_properties', None)
        typesUsingViewUrl = site_properties.getProperty(
            'typesUseViewActionInListings', ())

        for item in result:
            # #13771 commented this check introduced in changeset 12733 since
            # auto-content is being called from video_popup_view which adds
            # Article as portal_type to check and auto-context calls sameTheme

            # skip articles from auto related by theme since they are related
            # by publication group
            # if item.portal_type == 'Article':
            #    continue


            # check if path isn't the same between brain and context instead
            # of getId since we can have results that have the same id but not
            # path for instance in videos there are multiple 'video-file' ids
            if item.getPath() != self.context.absolute_url(1):
                commonThemesIds = [theme for theme in item.getThemes
                                   if theme in contextThemes]
                # info = getObjectInfo(item.getObject(), self.request)
                # pass typesUsingViewUrl to getBrainInfo so we no longer have
                # to wake up objects for getting the urlview
                info = getBrainInfo(item, plone_utils, typesUsingViewUrl)
                info['commonThemesIds'] = commonThemesIds
                related.append(info)

        return related

    def autoContext(self, portal_type=None, fill_limit=None):
        """NOTE: returns full info. May end up being slow
        """
        fill_limit = fill_limit or 25
        refs = IRelations(self.context).autoContextReferences(portal_type)
        refs = [getObjectInfo(i, self.request) for i in refs]
        defaultConstraints = {'review_state': 'published',
                              'sort_limit': fill_limit}
        theme = self.sameTheme(portal_type, constraints=defaultConstraints)
        items = refs + theme
        items_len = len(items)
        if items_len < fill_limit:
            # add the remainder of fill_limit - items length to the original
            # fill_limit if we need more items
            defaultConstraints['sort_limit'] = fill_limit + (fill_limit -
                                                             items_len)
            items += self.sameType(portal_type, constraints=defaultConstraints)
        nondups = filterDuplicates(items)
        return nondups

    def sameType(self, portal_type=None, constraints=None):
        """
        NOTE: returns incomplete info, from getBrainInfo. You need to call
        annotateBrainInfo() if you need full info

        TODO: this should be made a private methods, not callable through
        the normal API, to emphasize that it doesn't return full info.

        """
        if not portal_type:
            portal_type = self.context.portal_type
        defaultConstraints = {'review_state': 'published'}
        if constraints:
            defaultConstraints.update(constraints)

        result = IRelations(self.context).getItems(
            portal_type,
            getBrains=True,
            considerDeprecated=True,
            constraints=defaultConstraints
        )
        related = others(self.context, result)

        # for item in related:
        ##obj = item.getObject()
        # if item.getId != cid:
        ##info = getObjectInfo(obj, self.request)
        # info = getBrainInfo(item, self.request)
        # related.append(info)

        return related

    def sameTypeByPublicationGroup(self):
        """ for now we don't group by publication group,
            we only return all of same
            type that can have a publication group.
        """
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).byPublicationGroup(
            samePortalType=True,
            getBrains=True,
            constraints=constraints)

        related = others(self.context, result)
        annotateThemeInfos(related, self.request)
        # Note: enable if you notice errors about missing keys

        # for item in result:
        # obj = item.getObject()
        # if item.getId != self.context.getId():
        # info = getObjectInfo(obj, self.request)
        # related.append(info)

        return related

    def _contextThemes(self):
        """ Themes
        """
        theme = queryAdapter(self.context, IThemeTagging)
        if theme is None:
            contextThemes = []
        else:
            # 13986 ExternalDataSpec Theme doesn't have nondepregated_tags
            contextThemes = getattr(theme, 'nondeprecated_tags', None)
            if not contextThemes:
                contextThemes = theme.tags
        return contextThemes


class DocumentRelated(BrowserView):
    """ DocumentRelated BrowserView """

    implements(IDocumentRelated)

    def __init__(self, context, request):
        super(DocumentRelated, self).__init__(context, request)

        # self.context = utils.context(self)
        self.plone_utils = getToolByName(context, 'plone_utils')
        self.normalize = self.plone_utils.normalizeString

        self.portal_props = getToolByName(context, 'portal_properties')
        self.wf_tool = getToolByName(context, 'portal_workflow')
        self.site_props = self.portal_props.site_properties
        self.use_view = getattr(self.site_props,
                                'typesUseViewActionInListings', [])

        self.related = IRelations(self.context).references()

        self.related_feeds = []
        self.related_pages = []
        self.related_media_with_player = []
        self.related_other = []
        self.related_images = []
        for item in self.related:
            if MIVideo.providedBy(item):
                self.related_media_with_player.append(item)
            elif item.portal_type == 'Image':
                self.related_images.append(item)
            elif item.portal_type in ['Document', 'Highlight', 'PressRelease',
                                      'Speech', 'AssessmentPart']:
                self.related_pages.append(item)
            else:
                self.related_other.append(item)

    def _all_media(self):
        """ All media
        """
        return self.related_media_with_player + self.related_images

    def bottom_media(self):
        """ Bottom media
        """
        media = {}
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        popup = '/++resource++videoimages/popup_play_icon.png'
        for item in self.related_media_with_player[TOP_VIDEOS:] + \
                self.related_images:
            url = item.absolute_url()
            if item.portal_type in self.use_view:
                url += '/view'
            link = {'url': url, 'text': item.Title(),
                    'date': item.ModificationDate(),
                    'popup_icon': portal.absolute_url() + popup,
                    'has_media_player': True if queryAdapter(item, MIVideo)
                        else False,
                    'popup-url': item.absolute_url() +
                         '/flashfile_popup_window' if item.portal_type ==
                         'FlashFile' else item.absolute_url() +
                                          '/popup-play.html'}

            category = IMediaType(item).types[0]
            if not media.has_key(category):
                media[category] = []
            media[category].append(link)

        for category, links in media.items():
            links.sort(cmp=lambda x, y: cmp(x['date'], y['date']))

        categories = media.keys()
        media_list = []
        for category in MEDIA_ORDER:
            if category in categories:
                media_list.append({'title': category.capitalize() + 's',
                                   'links': media[category]})
        for category in [cat for cat in categories if cat not in MEDIA_ORDER]:
            media_list.append({'title': category.capitalize() + 's',
                               'links': media[category]})
        return media_list

    def mediacount(self):
        """ Count
        """
        return len(self._all_media())

    def multimedia(self):
        """ Multimedia
        """
        # TODO: delete? Where's this used?
        # multimedia = []
        for item in self.related_media_with_player:
            mimetype = item.get_content_type()
            player_html = queryAdapter(item, name=mimetype,
                                       interface=IMediaPlayer)
            player_html.max_width = 200 - 16
            player_html.autoplay = False
            player_html.autobuffer = False
            return player_html(None, None)
        return None

    def pages(self):
        """ Pages
        """
        pages = []
        for item in self.related_pages:
            pages.append({'title': item.Title(),
                          'url': item.absolute_url()})
        return pages

    def other(self):
        """ Other
        """
        other = []

        for item in self.related_other:
            item_type_class = self.normalize(item.portal_type)
            item_wf_state = self.wf_tool.getInfoFor(item, 'review_state', '')
            item_wf_state_class = 'state-' + self.normalize(item_wf_state)

            urlview = getMultiAdapter((item, self.request), name="url")
            imgview = queryMultiAdapter((item, self.request), name="imgview")
            url = urlview.listing_url()

            other.append({'title': item.Title(),
                          'description': item.Description(),
                          'url': url,
                          'absolute_url': item.absolute_url(),
                          'item_type': item.portal_type,
                          'item_type_class': item_type_class,
                          'item_wf_state': item_wf_state,
                          'item_wf_state_class': item_wf_state_class,
                          'is_video': MIVideo.providedBy(item),
                          'has_img': (imgview is not None and
                                      imgview.display() is True)
                          })
        return other

    def top_count(self):
        """ Top count
        """
        return len(self.top_media())

    def top_media(self):
        """ Top media
        """
        media = []

        for item in self.related_media_with_player[:TOP_VIDEOS]:
            info = getObjectInfo(item, self.request)
            media.append(info)
        return media
