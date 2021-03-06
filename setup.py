""" EEA Content Types installer
"""
import os
from setuptools import setup, find_packages

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
          'eea.mediacentre',
          'eea.themecentre',
          'eea.translations',
          'eea.promotion',
          'eea.vocab',
          'eea.depiction',
          'eea.daviz',
          'Products.EEAPloneAdmin',
          'Products.NavigationManager',

          'rdflib',
          'pika',
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
          'valentine.linguaflow',
          'eventlet',

          'eea.rabbitmq.client'
          #obsolete
          #'Products.CMFSquidTool',

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
