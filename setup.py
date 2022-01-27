'''
File manifest generator for files. Checks for common
data attributes
'''
import ast
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#https://thepythonguru.com/writing-packages-in-python/
def get_version(version_tuple):
    '''Get version from module'''
    if not isinstance(version_tuple[-1], int):
        return '.'.join(
            map(str, version_tuple[:-1])
        ) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))

INIT = os.path.join(
    os.path.dirname(__file__), 'fcheck.py')

VERSION_LINE = list(
    filter(lambda l: l.startswith('VERSION'), open(INIT))
)[0]

PKG_VERSION = get_version(ast.literal_eval(VERSION_LINE.split('=')[-1].strip()))

def readme():
    '''
    Read in the markdown long description
    '''
    try:
        with open( os.path.join(
                   os.path.dirname(__file__),
                   'README.md')) as fil:
            return fil.read()
    except IOError:
        return ''
CONFIG = {
    'description': 'File manifest generator',
    'long_description': readme(),
    'long_description_content_type' : 'text/markdown',
    'author': 'Paul Lesack',
    'license': 'MIT',
    'url': 'https://ubc-library-rc.github.io/fcheck/',
    'download_url': 'https://github.com/ubc-library-rc/fcheck',
    'author_email': 'paul.lesack@ubc.ca',
    'py_modules': ['fcheck'],
    'python_requires': '>=3.6',
    'install_requires' : ['pyreadstat>=1.1.0'],
    'scripts':['scripts/damage.py'],
    'name': 'fcheck',
    'version': PKG_VERSION,
    'classifiers' : ['Development Status :: 4 - Beta',
                     'Intended Audience :: Education',
                     'License :: OSI Approved :: MIT License'
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Topic :: Education'],
    'project_urls' : {'Documentation': 'https://ubc-library-rc.github.io/fcheck',
                      'Source': 'https://github.com/ubc-library-rc/fcheck',
                      'Tracker': 'https://github.com/ubc-library-rc/fcheck/issues'},
    'keywords' : ['metadata','SAS', 'SPSS', 'Stata', 'rectangular files', 'manifest generator'],
    }
setup(**CONFIG)
