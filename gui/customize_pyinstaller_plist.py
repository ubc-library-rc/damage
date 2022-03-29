'''
Instead of creating a MacOS Pyinstaller bundle, create a non-windowed, non-standalone
app by running PyInstaller *not* from a spec

python310 -m PyInstaller   --add-binary='/System/Library/Frameworks/Tk.framework/Tk':'tk' --add-binary='/System/Library/Frameworks/Tcl.framework/Tcl':'tcl' --additional-hooks-dir ../py_install/ --icon=assets/DamageAppIcon.icns src/damage_gui.py --osx-bundle-identifier=ca.ubc.library --target-arch=x86_64 --noconsole

Then run this script, which edits the created plist and makes it so it doesn't have to uncompress
into a temporary directory. Hence it runs faster. I am not sure why this isn't the default behaviour.

Of course, any other plist entries can also be added.

Once this is run on the compiled application, the app can be packaged into a DMG
'''



import os
import plistlib
import sys

here = os.getcwd()
os.chdir(os.path.dirname(__file__))
from src.damage_gui import VERSION
os.chdir(here)

try:
    dm_plist_p = sys.argv[1]
except:
    dm_plist_p = (os.path.dirname('__file__') +
                  os.path.join('dist','damage_gui.app','Contents','Info.plist'))

with open(dm_plist_p, 'rb') as f:
    dm_plist = plistlib.load(f)

dm_plist['CFBundleDisplayName'] = 'Damage' #This controls what the app is called. ie, value.app
#Weirdly, a terminal ls still shows damage_gui.app, but Finder shows Damage.app
dm_plist['CFBundleName'] = 'Damage'  # This controls the menu name and the version string
dm_plist['CFBundleShortVersionString'] = '.'.join(map(str, VERSION))
dm_plist['NSPrincipalClass'] = 'NSApplication'
dm_plist['NSAppleScriptEnabled'] = False
dm_plist['CFBundleDocumentTypes']=[
	       		{
	       		    #'CFBundleTypeIconFile': 'Contents/Resources/DamageAppIcon.icns',
	       		    'LSHandlerRank': 'Alternate',
       			    'CFBundleTypeRole': 'Editor'
	       		    }]
with open(dm_plist_p, 'wb') as f:
    plistlib.dump(dm_plist, f)
