# -*- mode: python ; coding: utf-8 -*-
import sys
from src.damage_gui import VERSION

block_cipher = None

if sys.platform == 'darwin':
             binaries=[('/System/Library/Frameworks/Tk.framework/Tk', 'tk'), ('/System/Library/Frameworks/Tcl.framework/Tcl', 'tcl')]
else:
             binaries=[]

a = Analysis(['src/damage_gui.py'],
             pathex=[],
             binaries=binaries,
             datas=[],
             hiddenimports=[],
             hookspath=['../py_install/'],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='Damage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='assets/DamageAppIcon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='damage_gui')
app = BUNDLE(coll,
             name='Damage.app',
             icon='assets/DamageAppIcon.icns',
             bundle_identifier='ca.ubc.library',
	     version='.'.join(map(str,VERSION)),
	     info_plist={
	       	    'NSPrincipalClass': 'NSApplication',
	       	    'NSAppleScriptEnabled': False,
	       	    'CFBundleDocumentTypes': [
	       		{
	       		    #'CFBundleTypeName': 'My File Format',
	       		    'CFBundleTypeIconFile': 'assets/DamageAppIcon.icns',
	       		    '#LSItemContentTypes': ['com.example.myformat'],
	       		    'LSHandlerRank': 'Alternate',
			    'CFBundleTypeRole': 'Editor'
	       		    }
	       		]
	       	    }
)
