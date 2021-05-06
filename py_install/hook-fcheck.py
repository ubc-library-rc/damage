'''
Adds required submodules for Pyinstaller construction of
damage manifest generator.

https://github.com/ubc-library-rc/fcheck
'''

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('pyreadstat')
hiddenimports += ['pandas', 'multiprocessing']

