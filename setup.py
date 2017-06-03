
import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README')).read()

version = open("VERSION").readline().strip()

install_requires = [
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='PySPG',
      version=version,
      description="Python Systematic Parameter Generator",
      long_description=README,
      classifiers=[
          # Get strings from
          # http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='simulations parameters optimisation',
      author='Claudio J. Tessone',
      author_email='claudio.tessone@uzh.ch',
      url='https://github.com/tessonec/PySPG',
      packages=['spg.base', 'spg.cmdline', 'spg.master', 'spg.plot',
                'spg.runner', 'spg.simulation', 'spg.utils', 'spg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      scripts=['scripts/spg-db.py', 'scripts/spg-plotter.py',
               'scripts/spg-run-standalone.py',
               'scripts/spg-run-threaded.py', 'scripts/spg-table.py'],
      test_suite='tests')
