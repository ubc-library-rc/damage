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

CONFIG = {
    'description': 'File manifest generator',
    'author': 'Paul Lesack',
    'license': 'MIT',
    'url': 'https://ubc-library-rc.github.io/fcheck/',
    'download_url': 'https://github.com/ubc-library-rc/fcheck',
    'author_email': 'paul.lesack@ubc.ca',
    'modules': ['fcheck'],
    'install_requires' : ['pyreadstat>=1.1.0'],
    'scripts':['scripts/damage.py'],
    'name': 'fcheck',
    'version': PKG_VERSION
}

setup(**CONFIG)
