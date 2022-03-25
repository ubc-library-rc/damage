# -*- mode: python ; coding: utf-8 -*-

from src.damage_gui import VERSION

block_cipher = None


a = Analysis(['src/damage_gui.py'],
             pathex=[],
             binaries=[('/System/Library/Frameworks/Tk.framework/Tk', 'tk'), ('/System/Library/Frameworks/Tcl.framework/Tcl', 'tcl')],
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
          [],
          exclude_binaries=True,
          name='damage_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch='x86_64',
          codesign_identity=None,
          entitlements_file=None , icon='assets/DamageAppIcon.icns')
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
