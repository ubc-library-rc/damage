'''
File manifest generator for files. Checks for common
data attributes
'''
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

init = os.path.join(
    os.path.dirname(__file__), 'mgen.py')

version_line = list(
    filter(lambda l: l.startswith('VERSION'), open(init))
)[0]

PKG_VERSION = get_version(eval(version_line.split('=')[-1]))

CONFIG = {
    'description': 'File manifest generator',
    'author': 'Paul Lesack',
    'license': 'MIT',
    'url': 'https://ubc-library-rc.github.io/mgen/',
    'download_url': 'https://github.com/ubc-library-rc/mgen',
    'author_email': 'paul.lesack@ubc.ca',
    'modules': ['mgen'],
    #'scripts':['scripts/dryadd.py'],
    'name': 'mgen',
    'version': PKG_VERSION
}

setup(**CONFIG)
