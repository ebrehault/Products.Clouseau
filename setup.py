from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "Clouseau", "version.txt")).read().strip()

setup(name='Products.Clouseau',
      version=version,
      description="An Ajax based Zope/Python prompt for Plone",
      long_description=open(os.path.join("Products", "Clouseau", "README.txt")).read().decode('UTF8').encode('ASCII', 'replace'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone"
        ],
      keywords='Plone Clouseau AJAX',
      author='Andy McKay',
      author_email='andy@clearwind.ca',
      url='http://plone.org/products/clouseau',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
