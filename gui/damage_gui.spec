# -*- mode: python ; coding: utf-8 -*-

from src.damage_gui import VERSION

block_cipher = None


a = Analysis(['src/damage_gui.py'],
             pathex=[],
             binaries=[('/System/Library/Frameworks/Tk.framework/Tk', 'tk'), ('/System/Library/Frameworks/Tcl.framework/Tcl', 'tcl')],
             datas=[],
             hiddenimports=[],
             hookspath=['/Users/paul/Documents/Work/Projects/fcheck/py_install/'],
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
          target_arch='x86_64',
          codesign_identity=None,
          entitlements_file=None , icon='assets/DamageAppIcon.icns')
#https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/CoreFoundationKeys.html#//apple_ref/doc/uid/20001431-101685
app = BUNDLE(exe,
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
