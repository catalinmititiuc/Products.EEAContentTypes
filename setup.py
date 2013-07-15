""" EEA Content Types installer
"""
from setuptools import setup, find_packages
import os

NAME = 'Products.EEAContentTypes'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="EEA logic and content types",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
           "Framework :: Plone",
           "Programming Language :: Python",
           "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea',
      author='European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url="https://svn.eionet.europa.eu/projects/"
          "Zope/browser/trunk/Products.EEAContentTypes",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',

          'Products.LinguaPlone',
          'Products.ATVocabularyManager',
          'Products.OrderableReferenceField',
          'Products.RedirectionTool',

          'eea.rdfmarshaller',
          'eea.facetednavigation',
          'eea.forms',
          'eea.locationwidget',
          'eea.mediacentre',
          'eea.themecentre',
          'eea.translations',
          'eea.promotion',
          'eea.vocab',
          'eea.depiction',
          'Products.EEAPloneAdmin',
          'Products.NavigationManager',

          'p4a.video',
          'rdflib',
          'collective.monkeypatcher',
          'eea.reports',
          'eea.relations',

          'eea.cache',

          #required in tests
          'eea.dataservice',
          'eea.design',
          'eea.geotags',
          'eea.indicators',
          'eea.soer',
          'hachoir-core',   #only for the patch
          'valentine.linguaflow',

          #obsolete
          #'Products.CMFSquidTool',

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
