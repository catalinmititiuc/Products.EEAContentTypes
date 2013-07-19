""" Syndication tests
"""
from App.Common import package_home
from DateTime import DateTime
from Products.EEAContentTypes.config import product_globals
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from Products.CMFPlone.browser.syndication.adapters import IFeedItem
import os

image = open(os.path.join(package_home(
    product_globals), 'tests', 'image.png'), 'rb')
image = image.read()

location = '{"type": "FeatureCollection", "features": [{"geometry": '\
        '{"type": "Polygon", "coordinates": [[51.609926999999999, 10.'\
        '165984999999978], [51.609926999999999, 10.300237000000038], '\
        '[51.675878999999988, 10.300237000000038], [51.675878999999988,'\
        '10.165984999999978]]}, "type": "Feature", "bbox": [51.60992699'\
        '9999999, 10.165984999999978, 51.675878999999988, 10.30023700000'\
        '0038], "properties": {"description": "37197 Hattorf am Harz, Germany'\
        '", "tags": ["locality", "political"], "title": "Hattorf am Harz", '\
        '"name": "", "other": {"geometry": {"bounds": {"aa": {"b": 51.609926'\
        '999999999, "d": 51.675878999999988}, "Y": {"b": 10.300237000000038, '\
        '"d": 10.165984999999978}}, "location": {"Ka": 51.651370900000003, "La'\
        '": 10.235499699999991}, "viewport": {"aa": {"b": 51.609926999999999, '\
        '"d": 51.675878999999988}, "Y": {"b": 10.300237000000038, "d": 10.1659'\
        '84999999978}}, "location_type": "APPROXIMATE"}, "address_components":'\
        '[{"long_name": "Hattorf am Harz", "types": ["locality", "political"],'\
        '"short_name": "Hattorf am Harz"}, {"long_name": "Osterode", "types": '\
        '["administrative_area_level_2", "political"], "short_name": "Osterode'\
        '"}, {"long_name": "Niedersachsen", "types": ["administrative_area_lev'\
        'el_1", "political"], "short_name": "NDS"}, {"long_name": "Germany", "'\
        'types": ["country", "political"], "short_name": "DE"}, {"long_name": '\
        '"37197", "types": ["postal_code"], "short_name": "37197"}], "formatte'\
        'd_address": "37197 Hattorf am Harz, Germany", "types": ["locality", "'\
        'political"]}, "center": [51.651370900000003, 10.235499699999991]}}]}'
location = '37197 Hattorf am Harz, Germany'

class TestSyndication(EEAContentTypeTestCase):
    """ Test-cases for syndication. """

    def afterSetUp(self):
        """ Set up
        """
        self.setRoles('Manager')
        self.workflow = self.portal.portal_workflow
        self.effective_date = DateTime(year=2008, month=4, day=3)
        self.start_date = DateTime(year=2007, month=1, day=1)

        self.folder.invokeFactory('Document', id='doc')
        doc = self.folder.doc
        doc.setTitle('Some Document')
        doc.setEffectiveDate(self.effective_date)
        doc.reindexObject()

        self.folder.invokeFactory('QuickEvent', id='event')
        event = self.folder.event
        event.setTitle('Some Event')
        event.setLocation(location)
        event.setEffectiveDate(self.effective_date)
        event.setStartDate(self.start_date)
        event.reindexObject()

    def testTitle(self):
        """ Title
        """
        entry = IFeedItem(self.folder.doc)
        self.assertEquals(entry.getTitle(), 'Some Document')


        entry = IFeedItem(self.folder.event)
        # ichimdav location changes
        #'Some Event [37197 Hattorf am Harz, Germany]'
        self.assertEquals(entry.getTitle(),
                          'Some Event')

    def testDate(self):
        """ Date
        """
        entry = IFeedItem(self.folder.doc)
        self.assertEquals(entry.getEffectiveDate(), self.effective_date)

        entry = IFeedItem(self.folder.event)
        self.assertEquals(entry.getEffectiveDate(), self.start_date)

    def testFolderThumb(self):
        """ Folder thumb
        """
        # simulate publications which are folders
        self.folder.invokeFactory(
            'Image', id='img1', image=image, title='Simple Image')
        entry = IFeedItem(self.folder)
        self.failUnless('img' in entry.getBody())

    def testHighlightThumb(self):
        """ Highlight thumb
        """
        highlight = self.folder[self.folder.invokeFactory(
            'Highlight', id='h1',  title='Highlight')]
        highlight.setImage(image)
        entry = IFeedItem(highlight)
        self.failUnless('img' in entry.getBody())


def test_suite():
    """ Suite
    """
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestSyndication))
