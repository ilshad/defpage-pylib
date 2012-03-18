import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'Paste',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='defpage.lib',
      version='0.1',
      description='defpage shared lib',
      long_description=README + '\n\n' +  CHANGES,
      packages=find_packages(),
      namespace_packages=['defpage'],
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require = requires,
      test_suite="defpage.lib",
      entry_points = """\
      [paste.app_factory]
      main = defpage.lib:main
      """,
      paster_plugins=['pyramid'],
      )
